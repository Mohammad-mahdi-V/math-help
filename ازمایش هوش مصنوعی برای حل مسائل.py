import google.generativeai as genai
import tkinter as tk
from tkinter import ttk
import sv_ttk
import os
import atexit
import ctypes
import sys
import subprocess
import threading

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
# کلید API را جایگزین کنید
genai.configure(api_key="AIzaSyBCpiTAYNcd1qTIup_sfcI8lB9oI_klN9Y")

# پیام سیستم جهت دستورالعمل‌های مورد نظر
system_message = """
شما یک دستیار مفید به نام "ژوپیتر" هستید.
همیشه به فارسی پاسخ دهید.
تخصص شما در مباحث فیزیک و ریاضی است.
اگر کاربر سوالی غیر از مباحث فیزیک و ریاضی بپرسد، باید پاسخ دهید:
"فقط به سوالات فیزیک و ریاضی پاسخ می‌دهم."
هنگام نمایش کسرها، آن‌ها را به صورت (x)/(y) نمایش دهید.
در انتهای هر پاسخ، به صورت خودکار عبارت زیر را اضافه کنید:
"ساخته شده توسط گوگل و بازسازی شده توسط تیم ژوپیتر".
اگر کاربر بپرسد "ژوپیتر کد چیست؟"، پاسخ دهید:
"ژوپیتر کد توسط محمد امین سیفی و محمد مهدی وافری ساخته شده است."
"""

# تنظیمات تولید مدل
generation_config = {
    "temperature": 0.5,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 65536,
    "response_mime_type": "text/plain",
}

# مدل پیش‌فرض
default_model = "gemini-2.0-flash-thinking-exp-01-21"
current_model_name = default_model  # تعریف متغیر گلوبال برای نگهداری نام مدل فعلی

model = genai.GenerativeModel(
    model_name=default_model,
    generation_config=generation_config,
    tools='code_execution',
)

# -------------------------------
# تنظیم DNS
# -------------------------------
INTERFACE_NAME = "Wi-Fi"  # در صورت نیاز نام کارت شبکه را تغییر دهید

def set_dns():
    try:
        os.system(f'netsh interface ip set dns name="{INTERFACE_NAME}" static 10.202.10.202')
        print("✅ DNS روی 10.202.10.202 تنظیم شد.")
    except Exception as e:
        print(f"⚠ خطا در تنظیم DNS: {e}")

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
    global current_model_name
    # قالب‌بندی پیام کاربر
    if reply_to and not current_model_name == "tunedModels/z---gwdidy3wg436" :
        formatted_message = f"Replying to: '{reply_to}'\nUser: {user_message}"
    else:
        formatted_message = user_message
    chat_history.append({"role": "user", "message": formatted_message})
    
    # اگر مدل انتخاب‌شده "تربیت شده توسط ژوپیتر کد" باشد، پیام سیستم ارسال نمی‌شود.
    if current_model_name == "tunedModels/z---gwdidy3wg436":
        response = model.generate_content([msg["message"] for msg in chat_history])
    else:
        response = model.generate_content([system_message] + [msg["message"] for msg in chat_history])
    
    bot_reply = response.text.replace("Jupiter",("ژوپیتر")).replace("code",("کد"))
    chat_history.append({"role": "assistant", "message": bot_reply})
    return bot_reply

# -------------------------------
# کلاس برای نمایش پیام‌ها به صورت حباب‌های چت (ریسپانسیو)
# -------------------------------
class ChatFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        # ایجاد Canvas برای اسکرول کردن پیام‌ها
        self.canvas = tk.Canvas(self, borderwidth=0, background="#2E2E2E")
        self.frame = tk.Frame(self.canvas, background="#2E2E2E")
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        # ایجاد پنجره داخلی در canvas
        self.window_item = self.canvas.create_window((0, 0), window=self.frame, anchor="nw", tags="self.frame")
        # تنظیم ریسپانسیو بودن فریم داخلی
        self.canvas.bind("<Configure>", self.onCanvasConfigure)
        self.frame.bind("<Configure>", self.onFrameConfigure)
    
    def onFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def onCanvasConfigure(self, event):
        self.canvas.itemconfigure(self.window_item, width=event.width)
    
    def add_message(self, sender, message):
        # رنگ حباب: پیام‌های کاربر آبی، پیام‌های Gemini قرمز
        bubble_bg = "#007AFF" if sender == "You" else "#FF3B30"
        bubble = tk.Frame(self.frame, bg=bubble_bg, padx=10, pady=5)
        label = tk.Label(bubble, text=message, wraplength=400, justify="left",
                         bg=bubble_bg, font=("B Morvarid", 12), fg="white")
        label.pack()
        anchor_side = "w" if sender == "You" else "e"
        bubble.pack(fill="x", padx=10, pady=5, anchor=anchor_side)
        self.canvas.yview_moveto(1.0)
        return label

# -------------------------------
# رابط کاربری اصلی (Tkinter UI) با sv_ttk
# -------------------------------
window = tk.Tk()
window.title("Chat with Gemini")

# تنظیم تم تاریک با sv_ttk
sv_ttk.set_theme("dark")

# تعریف استایل برای Combobox به همراه فونت "B Morvarid"
style = ttk.Style(window)
style.configure("TCombobox", font=("B Morvarid", 12))
window.option_add('*TCombobox*Listbox.font', ("B Morvarid", 12))

# افزودن Combobox برای انتخاب مدل
model_label = ttk.Label(window, text="انتخاب مدل:", font=("B Morvarid", 12))
model_label.pack(padx=10, pady=(10, 0), anchor="w")

# لیست گزینه‌های نمایش داده شده به زبان فارسی به همراه نگاشت به مدل‌های واقعی
model_options_display = [
    "جمنای 1.5 فلاش",
    "جمنای 2 فلاش",
    "جمنای پرو 1.5",
    "مدل آموزش داده شده توسط ژوپیتر کد"
]
model_options_mapping = {
    "جمنای 1.5 فلاش": "gemini-1.5-flash-8b-exp-0924",
    "جمنای 2 فلاش": "gemini-2.0-flash-thinking-exp-1219",
    "جمنای پرو 1.5": "gemini-1.5-pro-exp-0827",
    "مدل آموزش داده شده توسط ژوپیتر کد": "tunedModels/z---gwdidy3wg436"
}

model_combobox = ttk.Combobox(window, values=model_options_display, font=("B Morvarid", 12))
model_combobox.current(1)  # پیشفرض: "جمنای 2 فلاش"
model_combobox.pack(padx=10, pady=(0, 10), fill="x")

def update_model(event):
    global model, current_model_name
    selected_display = model_combobox.get()
    actual_model = model_options_mapping.get(selected_display, "gemini-2.0-flash-thinking-exp-01-21")
    model = genai.GenerativeModel(actual_model)
    current_model_name = actual_model  # به‌روزرسانی نام مدل فعلی
    print(f"مدل انتخاب‌شده: {actual_model}")

model_combobox.bind("<<ComboboxSelected>>", update_model)

# ایجاد قاب اسکرول‌شونده برای نمایش پیام‌ها
chat_frame = ChatFrame(window)
chat_frame.pack(padx=10, pady=10, fill="both", expand=True)

# ورودی پیام کاربر (ttk.Entry)
input_entry = ttk.Entry(window, font=("B Morvarid", 12))
input_entry.pack(padx=10, pady=10, fill="x")

def handle_response(user_message, gemini_label):
    response = send_message(user_message)
    window.after(0, lambda: gemini_label.config(text=response))

def on_send():
    user_message = input_entry.get().strip()
    if user_message == "":
        return
    # افزودن پیام کاربر به چت
    chat_frame.add_message("You", user_message)
    # افزودن پیام موقت برای پاسخ ژوپیتر
    gemini_label = chat_frame.add_message("Gemini", "در حال ایجاد جواب ...")
    input_entry.delete(0, tk.END)
    # اجرای دریافت پاسخ به صورت غیرهمزمان (ترد)
    threading.Thread(target=handle_response, args=(user_message, gemini_label), daemon=True).start()

send_button = ttk.Button(window, text="Send", command=on_send)
send_button.pack(pady=10)

# هنگام بسته شدن پنجره، DNS به حالت اولیه برگردد
window.protocol("WM_DELETE_WINDOW", lambda: [reset_dns(), window.destroy()])

window.mainloop()
