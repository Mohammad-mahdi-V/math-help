import json
import uuid
from pathlib import Path
from cryptography.fernet import Fernet
import sqlite3
import bcrypt

class DatabaseManager:
    def __init__(self, db_name="app_database.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # ایجاد جدول کاربران
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                key VARCHAR,
                password TEXT
            )
        ''')
        
        
        # ایجاد جدول تاریخچه
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        self.conn.commit()
    
    def register_user(self, username, password):
                # هش کردن رمز عبور برای امنیت
        KEYS_FILE = "secure_keys.json"
        MASTER_KEY = Fernet.generate_key()
        # کلید اصلی برای رمزنگاری فایل کلیدها (امن نگه دار!)
        cipher = Fernet(MASTER_KEY)

        def load_keys():
            """خواندن کلیدهای رمزنگاری‌شده"""
            key_file = Path(KEYS_FILE)
            if not key_file.exists():
                return {}
            with open(key_file, 'rb') as f:
                encrypted_keys = f.read()
            try:
                keys = json.loads(cipher.decrypt(encrypted_keys).decode('utf-8'))
                return keys
            except:
                return {}

        def save_keys(keys):
            """ذخیره کلیدهای رمزنگاری‌شده"""
            encrypted_keys = cipher.encrypt(json.dumps(keys).encode('utf-8'))
            with open(KEYS_FILE, 'wb') as f:
                f.write(encrypted_keys)

        def generate_unique_key():
            """تولید کلید رندوم و یکتا"""
            keys = load_keys()
            while True:
                key = Fernet.generate_key()  # کلید 256 بیتی برای AES
                key_b64 = key.decode('utf-8')
                if key_b64 not in keys.values():
                    key_id = str(uuid.uuid4())
                    keys[key_id] = key_b64
                    save_keys(keys)
                    return key_id, key

        def encrypt(message):
            """رمزنگاری پیام با AES"""
            key_id, key = generate_unique_key()
            cipher_suite = Fernet(key)
            encrypted = cipher_suite.encrypt(message.encode('utf-8'))
            return encrypted.decode('utf-8'), key_id

        def decrypt(encrypted, key_id):
            """رمزگشایی با AES"""
            try:
                keys = load_keys()
                if key_id not in keys:
                    return f"Error: Key ID {key_id} not found"
                key = keys[key_id].encode('utf-8')
                cipher_suite = Fernet(key)
                decrypted = cipher_suite.decrypt(encrypted.encode('utf-8')).decode('utf-8')
                return decrypted
            except Exception as e:
                return f"Decryption error: {e}"

    def login_user(self, username, password):
        self.cursor.execute('SELECT id, password FROM users WHERE username = ?', (username,))
        user = self.cursor.fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[1]):
            return user[0]  # شناسه کاربر
        return None

    def save_history(self, user_id, action):
        self.cursor.execute('INSERT INTO history (user_id, action) VALUES (?, ?)', 
                          (user_id, action))
        self.conn.commit()

    def get_user_history(self, user_id):
        self.cursor.execute('SELECT action, timestamp FROM history WHERE user_id = ? ORDER BY timestamp DESC', 
                          (user_id,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
