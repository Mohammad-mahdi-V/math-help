import google.generativeai as genai
import tkinter as tk
from tkinter import ttk
import sv_ttk
import os
import atexit
import ctypes
import sys
import subprocess

# -------------------------------
# اجرای خودکار برنامه با دسترسی ادمین
# -------------------------------
def run_as_admin():
    """برنامه را با دسترسی ادمین اجرا می‌کند."""
    if ctypes.windll.shell32.IsUserAnAdmin():
        return  # اگر از قبل ادمین است، ادامه بده
    # اجرای مجدد برنامه با دسترسی ادمین
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

run_as_admin()

# -------------------------------
# تنظیمات Gemini و DNS
# -------------------------------
genai.configure(api_key="AIzaSyBCpiTAYNcd1qTIup_sfcI8lB9oI_klN9Y")  # کلید API خود را وارد کنید
model = genai.GenerativeModel("gemini-pro")

# نام کارت شبکه (Wi-Fi یا Ethernet)
INTERFACE_NAME = "Wi-Fi"  # در صورت نیاز نام کارت شبکه را تغییر دهید

# تنظیم DNS هنگام اجرا
def set_dns():
    try:
        os.system(f'netsh interface ip set dns name="{INTERFACE_NAME}" static 10.202.10.202')
        print("✅ DNS روی 10.202.10.202 تنظیم شد.")
    except Exception as e:
        print(f"⚠ خطا در تنظیم DNS: {e}")

# بازگردانی DNS به حالت اولیه هنگام خروج
def reset_dns():
    try:
        os.system(f'netsh interface ip set dns name="{INTERFACE_NAME}" dhcp')
        print("🔄 DNS به حالت اولیه برگشت.")
    except Exception as e:
        print(f"⚠ خطا در بازگردانی DNS: {e}")

atexit.register(reset_dns)
set_dns()

chat_history = []

def send_message(user_message, reply_to=None):
    formatted_message = user_message
    if reply_to:
        formatted_message = f"Replying to: '{reply_to}'\nUser: {user_message}"
    chat_history.append({"role": "user", "message": formatted_message})
    response = model.generate_content([msg["message"] for msg in chat_history])
    bot_reply = response.text
    chat_history.append({"role": "assistant", "message": bot_reply})
    return bot_reply

# -------------------------------
# کلاس برای نمایش پیام‌ها به صورت حباب‌های چت
# -------------------------------
class ChatFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        # ایجاد یک Canvas برای اسکرول کردن پیام‌ها
        self.canvas = tk.Canvas(self, borderwidth=0, background="#2E2E2E")
        self.frame = tk.Frame(self.canvas, background="#2E2E2E")
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw", tags="self.frame")
        self.frame.bind("<Configure>", self.onFrameConfigure)
    
    def onFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def add_message(self, sender, message):
        # تغییر رنگ حباب: پیام‌های کاربر آبی، پاسخ‌های Gemini قرمز
        bubble_bg = "#007AFF" if sender == "You" else "#FF3B30"
        bubble = tk.Frame(self.frame, bg=bubble_bg, padx=10, pady=5)
        label = tk.Label(bubble, text=message, wraplength=400, justify="left",
                         bg=bubble_bg, font=("B Morvarid", 12), fg="white")
        label.pack()
        # چینش پیام: پیام‌های کاربر در سمت چپ و پاسخ‌های مدل در سمت راست
        bubble.pack(fill="x", padx=10, pady=5, anchor="w" if sender=="You" else "e")
        self.canvas.yview_moveto(1.0)

# -------------------------------
# رابط کاربری اصلی (Tkinter UI) با sv_ttk
# -------------------------------
window = tk.Tk()
window.title("Chat with Gemini")

# تنظیم تم تاریک با sv_ttk
sv_ttk.set_theme("dark")

# ایجاد قاب اسکرول‌شونده برای نمایش پیام‌ها
chat_frame = ChatFrame(window)
chat_frame.pack(padx=10, pady=10, fill="both", expand=True)

# ورودی پیام کاربر (ttk.Entry) زیبا
input_entry = ttk.Entry(window, font=("B Morvarid", 12))
input_entry.pack(padx=10, pady=10, fill="x")

def on_send():
    user_message = input_entry.get().strip()
    if user_message == "":
        return
    # افزودن پیام کاربر به رابط چت
    chat_frame.add_message("You", user_message)
    response = send_message(user_message)
    # افزودن پاسخ مدل به رابط چت
    chat_frame.add_message("Gemini", response)
    input_entry.delete(0, tk.END)

send_button = ttk.Button(window, text="Send", command=on_send)
send_button.pack(pady=10)

# وقتی پنجره بسته شود، DNS به حالت اولیه برگردد
window.protocol("WM_DELETE_WINDOW", lambda: [reset_dns(), window.destroy()])

window.mainloop()
