import sqlite3
import os
import re
import bcrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import streamlit as st
# --- تنظیم کلید اصلی از محیط ---
MASTER_KEY = os.getenv("math_help_db_key")
if not MASTER_KEY:
    raise Exception("کلید اصلی (math_help_db_key) تنظیم نشده!")

def normalize_key(key_str):
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(key_str.encode())
    return digest.finalize()

MASTER_KEY_BYTES = normalize_key(MASTER_KEY)

def hash_identifier(identifier: str) -> bytes:
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(identifier.encode())
    return digest.finalize()

def encrypt_data(key: bytes, plaintext: bytes) -> bytes:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return nonce + ciphertext

def decrypt_data(key: bytes, encrypted_data: bytes) -> bytes:
    aesgcm = AESGCM(key)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None)

def is_password_strong(pw: str) -> bool:
    return (
        len(pw) >= 8 and
        re.search(r'[A-Z]', pw) and
        re.search(r'[a-z]', pw) and
        re.search(r'\d', pw) and
        re.search(r'[!@#$%^&*]', pw)
    )

EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

class DatabaseManager:
    def __init__(self, user_db_path="users.db", activity_db_path="activities.db"):
        self.user_conn = sqlite3.connect(user_db_path)
        self.activity_conn = sqlite3.connect(activity_db_path)
        self.setup()

    def setup(self):
        self.user_conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username BLOB NOT NULL,
                password BLOB NOT NULL,
                personal_key BLOB NOT NULL,
                user_email BLOB NOT NULL
            );
        ''')
        self.user_conn.commit()

        # چک کنیم آیا ستون username_hash وجود دارد یا نه
        cursor = self.user_conn.execute("PRAGMA table_info(users);")
        columns = [row[1] for row in cursor.fetchall()]
        if "username_hash" not in columns:
            self.user_conn.execute("ALTER TABLE users ADD COLUMN username_hash TEXT;")
            self.user_conn.commit()

        # جدول فعالیت‌ها
        self.activity_conn.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                activity_data BLOB NOT NULL,
                section_name BLOB NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        ''')
        self.activity_conn.commit()

    def register_user(self, username: str, password: str, email: str):
        username_hash = hash_identifier(username)
        cursor = self.user_conn.cursor()
        cursor.execute('SELECT 1 FROM users WHERE username_hash = ?', (username_hash,))
        if cursor.fetchone():
            raise Exception("این نام‌کاربری قبلاً ثبت شده است.")

        if not is_password_strong(password):
            raise Exception("رمز عبور باید قوی باشد.")

        if not EMAIL_REGEX.match(email):
            raise Exception("فرمت ایمیل نامعتبر است.")

        personal_key = os.urandom(32)
        encrypted_username = encrypt_data(MASTER_KEY_BYTES, username.encode())
        encrypted_personal_key = encrypt_data(MASTER_KEY_BYTES, personal_key)
        encrypted_email = encrypt_data(MASTER_KEY_BYTES, email.encode())
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        cursor.execute('''
            INSERT INTO users (username, username_hash, password, personal_key, user_email)
            VALUES (?, ?, ?, ?, ?)
        ''', (encrypted_username, username_hash, hashed_password, encrypted_personal_key, encrypted_email))
        self.user_conn.commit()
        return cursor.lastrowid

    def login_user(self, username: str, password: str):
        username_hash = hash_identifier(username)
        cursor = self.user_conn.cursor()
        cursor.execute('SELECT id, password, personal_key FROM users WHERE username_hash = ?', (username_hash,))
        row = cursor.fetchone()
        if not row:
            return "no user"

        user_id, stored_hashed_pw, encrypted_personal_key = row
        if not bcrypt.checkpw(password.encode('utf-8'), stored_hashed_pw):
            return "password not correct"

        return user_id

    def save_activity(self, user_id: int, activity_text: str, section: str):
        cursor = self.user_conn.execute('SELECT personal_key FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        if not result:
            raise Exception("کاربر پیدا نشد.")

        encrypted_personal_key = result[0]
        personal_key = decrypt_data(MASTER_KEY_BYTES, encrypted_personal_key)
        encrypted_activity = encrypt_data(personal_key, activity_text.encode())
        encrypted_section = encrypt_data(personal_key, section.encode())

        self.activity_conn.execute('''
            INSERT INTO activities (user_id, activity_data, section_name)
            VALUES (?, ?, ?)
        ''', (user_id, encrypted_activity, encrypted_section))
        self.activity_conn.commit()

    def get_user_activities(self, user_id: int):
        cursor = self.user_conn.execute('SELECT personal_key FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        if not result:
            raise Exception("کاربر پیدا نشد.")

        encrypted_personal_key = result[0]
        personal_key = decrypt_data(MASTER_KEY_BYTES, encrypted_personal_key)

        activities = []
        cursor = self.activity_conn.execute('SELECT activity_data FROM activities WHERE user_id = ?', (user_id,))
        for row in cursor.fetchall():
            decrypted_activity = decrypt_data(personal_key, row[0]).decode()
            activities.append(decrypted_activity)

        return activities

# ---- Streamlit UI ----
db = DatabaseManager()
st.title("صفحه آزمایشی Math Help")
menu = st.sidebar.selectbox("منوی اصلی", ["ورود", "ثبت نام", "ذخیره فعالیت", "نمایش فعالیت‌ها"])

if menu == "ثبت نام":
    st.header("ثبت نام کاربر جدید")
    username = st.text_input("نام کاربری")
    password = st.text_input("رمز عبور", type="password")
    email = st.text_input("ایمیل")
    if st.button("ثبت نام"):
        try:
            user_id = db.register_user(username, password, email)
            st.success(f"ثبت نام با موفقیت انجام شد. شناسه شما: {user_id}")
        except Exception as e:
            st.error(str(e))

elif menu == "ورود":
    st.header("ورود کاربر")
    username = st.text_input("نام کاربری")
    password = st.text_input("رمز عبور", type="password")
    if st.button("ورود"):
        result = db.login_user(username, password)
        if isinstance(result, int):
            st.session_state.user_id = result
            st.success("ورود با موفقیت انجام شد.")
        else:
            st.error(result)

elif menu == "ذخیره فعالیت":
    st.header("ذخیره فعالیت")
    if 'user_id' not in st.session_state:
        st.warning("ابتدا وارد شوید.")
    else:
        activity = st.text_area("متن فعالیت")
        section = st.text_input("بخش فعالیت")
        if st.button("ذخیره"):
            try:
                db.save_activity(st.session_state.user_id, activity, section)
                st.success("فعالیت با موفقیت ذخیره شد.")
            except Exception as e:
                st.error(str(e))

elif menu == "نمایش فعالیت‌ها":
    st.header("فعالیت‌های شما")
    if 'user_id' not in st.session_state:
        st.warning("ابتدا وارد شوید.")
    else:
        activities = db.get_user_activities(st.session_state.user_id)
        if activities:
            for idx, act in enumerate(activities, 1):
                st.write(f"{idx}. {act}")
        else:
            st.info("هیچ فعالیتی ذخیره نشده.")
