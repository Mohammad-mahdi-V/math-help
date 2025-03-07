import streamlit as st
import base64
import time
start_time = time.time()
import threading
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import venn
from itertools import combinations
from more_itertools.more import set_partitions
import os 
import tkinter as tk
import tkinter.ttk as ttk
import sv_ttk as sttk
import darkdetect
from tkinter import messagebox
import subprocess
import atexit
import ctypes
import sys
import pandas as pd
from google.generativeai.generative_models import GenerativeModel
from google.generativeai.client import configure
import re
import socket
import sympy as sp
import numpy as np
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import requests
import webbrowser
class SetsAlgorithm:
    
    def __init__(self, set_of_sets):
        """
        سازنده کلاس
        - اگر ورودی دیکشنری باشد، نام و مقادیر مجموعه‌ها را استخراج می‌کند.
        - در غیر این صورت، مجموعه‌ها را به صورت لیست از مجموعه تبدیل می‌کند.
        """
        if isinstance(set_of_sets, dict):
            self.set_of_sets = set_of_sets
            self.set_names = list(set_of_sets.keys())
            self.sets = list(set_of_sets.values())
        else:
            self.set_of_sets = set_of_sets
            self.set_names = [f"Set {i+1}" for i in range(len(set_of_sets))]
            self.sets = [set(s) for s in set_of_sets]
        self.num_sets = len(self.sets)

    
    @staticmethod
    def parse_set_string(s: str) -> str:
        """
        پردازش رشته ورودی مجموعه، تبدیل آن به فرمت قابل‌اجرا در eval
        """
        def parse_expr(s: str, i: int):
            tokens = []
            while i < len(s):
                if s[i].isspace():
                    i += 1
                    continue
                if s[i] == '{':
                    parsed_set, i = parse_set(s, i)
                    tokens.append(parsed_set)
                elif s[i] in "|&-()":
                    tokens.append(s[i])
                    i += 1
                else:
                    start = i
                    while i < len(s) and (s[i].isalnum() or s[i] == '_'):
                        i += 1
                    token = s[start:i]
                    tokens.append(token)  # دیگر نیازی به افزودن کوتیشن نیست
            return " ".join(tokens), i

        def parse_set(s: str, i: int):
            """
            پردازش مجموعه‌ها، تبدیل مجموعه‌های تو در تو به frozenset و حذف عناصر تکراری
            """
            i += 1  # رد کردن '{'
            elements = []  # لیست برای ذخیره اعضا
            current_chars = []
            while i < len(s):
                if s[i].isspace():
                    i += 1
                    continue
                if s[i] == '{':
                    if current_chars:
                        token = "".join(current_chars).strip()
                        if token:
                            elements.append(token)  # دیگر نیازی به افزودن کوتیشن نیست
                        current_chars = []
                    nested_set, i = parse_set(s, i)
                    elements.append(f"frozenset({nested_set})")  # نباید داخل {} اضافه شود
                elif s[i] == '}':
                    if current_chars:
                        token = "".join(current_chars).strip()
                        if token:
                            elements.append(token)  # دیگر نیازی به افزودن کوتیشن نیست
                    i += 1
                    break
                elif s[i] == ',':
                    if current_chars:
                        token = "".join(current_chars).strip()
                        if token:
                            elements.append(token)  # دیگر نیازی به افزودن کوتیشن نیست
                        current_chars = []
                    i += 1
                else:
                    current_chars.append(s[i])
                    i += 1
            inner = ", ".join(elements)
            return f"{{{inner}}}", i

        parsed, _ = parse_expr(s, 0)
        parsed = parsed if parsed != "{}" else "set()"  # جلوگیری از NameError
        return parsed


    @staticmethod
    def fix_set_variables(expression: str) -> str:
        """
        تبدیل متغیرهای غیرعددی داخل مجموعه‌ها و زیرمجموعه‌ها به رشته،
        به‌طوری که اگر یک عنصر قبلاً در کوتیشن قرار نگرفته باشد، آن را در کوتیشن قرار می‌دهد.
        """
        result = []
        token = ""
        brace_level = 0  # برای پیگیری سطح آکولاد
        i = 0
        while i < len(expression):
            ch = expression[i]
            # نادیده گرفتن فاصله‌های خالی
            if ch.isspace():
                i += 1
                continue

            # اگر کاراکتر شروع کوتیشن است، کل رشته کوتیشن‌دار را جمع‌آوری می‌کنیم
            if ch == '"':
                token += ch
                i += 1
                while i < len(expression) and expression[i] != '"':
                    token += expression[i]
                    i += 1
                if i < len(expression):
                    token += expression[i]  # اضافه کردن کوتیشن پایانی
                    i += 1
                continue

            # اگر آکولاد باز باشد
            if ch == '{':
                # قبل از اضافه کردن آکولاد، توکن جاری را پردازش می‌کنیم
                if token:
                    fixed_token = token.strip()
                    if brace_level > 0 and fixed_token and not fixed_token.isdigit() and not (fixed_token.startswith('"') and fixed_token.endswith('"')):
                        fixed_token = f'"{fixed_token}"'
                    result.append(fixed_token)
                    token = ""
                brace_level += 1
                result.append(ch)
                i += 1
                continue

            # اگر آکولاد بسته باشد
            elif ch == '}':
                if token:
                    fixed_token = token.strip()
                    if brace_level > 0 and fixed_token and not fixed_token.isdigit() and not (fixed_token.startswith('"') and fixed_token.endswith('"')):
                        fixed_token = f'"{fixed_token}"'
                    result.append(fixed_token)
                    token = ""
                result.append(ch)
                brace_level -= 1
                i += 1
                continue

            # اگر جداکننده (مثل کاما یا عملگرها) باشد
            elif ch == ',' or ch in "|&-()":
                if token:
                    fixed_token = token.strip()
                    if brace_level > 0 and fixed_token and not fixed_token.isdigit() and not (fixed_token.startswith('"') and fixed_token.endswith('"')):
                        fixed_token = f'"{fixed_token}"'
                    result.append(fixed_token)
                    token = ""
                result.append(ch)
                i += 1
                continue

            # در غیر این صورت، کاراکتر را به توکن اضافه می‌کنیم
            else:
                token += ch
                i += 1

        # پردازش توکن باقی‌مانده در انتها
        if token:
            fixed_token = token.strip()
            if brace_level > 0 and fixed_token and not fixed_token.isdigit() and not (fixed_token.startswith('"') and fixed_token.endswith('"')):
                fixed_token = f'"{fixed_token}"'
            result.append(fixed_token)
            
        return "".join(result)


    @staticmethod
    def to_frozenset(obj):
        """
        تبدیل یک شی (در صورت اینکه مجموعه یا frozenset باشد) به frozenset.
        این تابع به صورت بازگشتی روی عناصر اعمال می‌شود.
        """
        if isinstance(obj, (set, frozenset)):
            return frozenset(SetsAlgorithm.to_frozenset(x) for x in obj)
        return obj

    @staticmethod
    def subsets_one_set(given_set):
        """
        محاسبه زیرمجموعه‌های یک مجموعه.
        - در صورت طول مجموعه بزرگتر از 10، فقط 10 دسته زیرمجموعه را محاسبه می‌کند.
        """
        num_loop = 0
        if not isinstance(given_set, str):
            given_set = repr(given_set)
        given_set = eval(given_set)
        # ایجاد دیکشنری برای ذخیره زیرمجموعه‌ها
        if len(given_set) >= 11:
            subsets_dict = {f" زیرمجموعه{i}عضوی": [] for i in range(11)}
        else:
            subsets_dict = {f" زیرمجموعه{i}عضوی": [] for i in range(len(given_set)+1)}
        for i in range(len(given_set) + 1):
            if num_loop > 10:
                break
            for subset in combinations(given_set, i):
                subsets_dict[f" زیرمجموعه{i}عضوی"].append(subset)
            num_loop += 1
        return subsets_dict

    @staticmethod
    def partitions(given_set):
        """
        محاسبه افرازهای مجموعه
        - در صورت مجموعه‌های کوچکتر از 6 عضو، همه افرازها را بازمی‌گرداند.
        - در غیر این صورت، بیشترین 100 افراز را برمی‌گرداند.
        """
        if len(given_set) <= 5:
            return list(set_partitions(given_set))
        else:
            partition_list = []
            partition_loop = 0
            for partition in set_partitions(given_set):
                if partition_loop <= 100:
                    partition_list.append(partition)
                    partition_loop += 1
                else:
                    break
            return partition_list

    def U(self, bitmask):
        """
        محاسبه اتحاد مجموعه‌ها بر اساس بیت‌ماس.
        - مجموعه‌هایی که در بیت‌ماس انتخاب شده‌اند را اتحاد می‌کند.
        """
        return set().union(*(self.sets[i] for i in range(self.num_sets) if bitmask & (1 << i)))

    def I(self, bitmask):
        """
        محاسبه اشتراک مجموعه‌ها بر اساس بیت‌ماس.
        - تنها مجموعه انتخاب شده در بیت‌ماس را در نظر می‌گیرد.
        """
        selected_sets = [self.sets[i] for i in range(self.num_sets) if bitmask & (1 << i)]
        return set.intersection(*selected_sets)

    def Ms(self, bitmask, target_bit):
        """
        محاسبه تفاضل مجموعه:
        - از مجموعه هدف، سایر مجموعه‌های انتخاب شده (با حذف هدف) را کم می‌کند.
        """
        main_set = self.sets[target_bit]
        other_sets = self.U(bitmask & ~(1 << target_bit))
        return main_set - other_sets

    def check_other_information(self):
        """
        بررسی اطلاعات دیگر بین مجموعه‌ها از جمله زیرمجموعه بودن و عدم زنجیره‌ای بودن.
        """
        info = {
            "subsets_info": {
                f"Set {self.set_names[i]}": {
                    f"Set {self.set_names[j]}": set(self.sets[i]).issubset(set(self.sets[j]))
                    for j in range(self.num_sets) if i != j
                }
                for i in range(self.num_sets)
            },
            "all_sets_chain": all(
                set(self.sets[i]).issubset(set(self.sets[j])) or set(self.sets[j]).issubset(set(self.sets[i]))
                for i in range(self.num_sets) for j in range(i + 1, self.num_sets)
            )
        }

        info["all_sets_antychain"] = not info["all_sets_chain"]
        return info



    def U_I_Ms_advance(self, text):

        # جایگزینی علائم ∩ و ∪ با معادل‌های Python
        text = text.replace('∩', '&').replace('∪', '|')

        # اصلاح متغیرهای داخل مجموعه‌ها
        text = SetsAlgorithm.fix_set_variables(text)

        # استخراج قسمت‌هایی که خارج از `{}` هستند
        outside_braces = re.split(r'\{[^{}]*\}', text)  # فقط بخش‌های بیرون از `{}` را جدا می‌کند.
        found_vars = re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', " ".join(outside_braces))  # استخراج نام متغیرها
        # بررسی اینکه آیا متغیرهای **خارج از `{}`** در `self.set_of_sets` تعریف شده‌اند
        for var in found_vars:
            if var.upper() not in self.set_of_sets:
                messagebox.showerror("خطا", f"متغیر '{var}' تعریف نشده است!")
                return "در انتظار دریافت عبارت..."  # برای جلوگیری از هنگ کردن، مقدار پیش‌فرض بازگردانی شود.

        # تبدیل رشته‌ی ورودی به فرم پردازش‌شده
        transformed_text = SetsAlgorithm.parse_set_string(text)

        # تعریف متغیرهای موجود
        variables = {name: frozenset(set_val) for name, set_val in self.set_of_sets.items()}
        # اضافه کردن نسخه‌های با حروف کوچک
        variables.update({name.lower(): frozenset(set_val) for name, set_val in self.set_of_sets.items()})

        try:
            result = eval(transformed_text, {"__builtins__": {}, "frozenset": frozenset}, variables)
            return self.set_to_str(result)
        except Exception as e:
            messagebox.showerror("خطا در پردازش", f"خطا در ارزیابی عبارت:\n{e}")
            return "در انتظار دریافت عبارت..."


    @staticmethod
    def set_to_str(result):
        """
        تبدیل نتیجه مجموعه به رشته:
        - فرمت خروجی به صورتی است که اعضای مجموعه ها به صورت ساده و بدون کوتیشن یا آکولاد نمایش داده شوند.
        """
        if isinstance(result, frozenset):
            return "{" + ", ".join(str(item) if not isinstance(item, frozenset) else SetsAlgorithm.set_to_str(item) for item in result) + "}"
        elif isinstance(result, set):
            return "{" + ", ".join(str(item) if not isinstance(item, frozenset) else SetsAlgorithm.set_to_str(item) for item in result) + "}"
        else:
            return str(result)

    def draw_venn(self):
        
        """
        رسم نمودار ون برای دو یا سه مجموعه.
        """
        if self.num_sets == 3:
            # ارزیابی هر مجموعه با استفاده از safe_eval
            set_one = SetsAlgorithm.safe_eval(self.sets[0])
            set_two = SetsAlgorithm.safe_eval(self.sets[1])
            set_three = SetsAlgorithm.safe_eval(self.sets[2])
            subsets = {
                '100': len(set(set_one) - set(set_two) - set(set_three)),
                '010': len(set(set_two) - set(set_one) - set(set_three)),
                '110': len(set(set_one) & set(set_two) - set(set_three)),
                '001': len(set(set_three) - set(set_one) - set(set_two)),
                '101': len(set(set_one) & set(set_three) - set(set_two)),
                '011': len(set(set_two) & set(set_three) - set(set_one)),
                '111': len(set(set_one) & set(set_two) & set(set_three))
            }
            venn_obj = venn3(subsets=subsets, set_labels=(self.set_names[0], self.set_names[1], self.set_names[2]))
            if venn_obj.get_label_by_id('100'):
                venn_obj.get_label_by_id('100').set_text(
                    SetsAlgorithm.set_to_str(set(set_one) - set(set_two) - set(set_three))
                )
            if venn_obj.get_label_by_id('010'):
                venn_obj.get_label_by_id('010').set_text(
                    SetsAlgorithm.set_to_str(set(set_two) - set(set_one) - set(set_three))
                )
            if venn_obj.get_label_by_id('110'):
                venn_obj.get_label_by_id('110').set_text(
                    SetsAlgorithm.set_to_str(set(set_one) & set(set_two) - set(set_three))
                )
            if venn_obj.get_label_by_id('001'):
                venn_obj.get_label_by_id('001').set_text(
                    SetsAlgorithm.set_to_str(set(set_three) - set(set_one) - set(set_two))
                )
            if venn_obj.get_label_by_id('101'):
                venn_obj.get_label_by_id('101').set_text(
                    SetsAlgorithm.set_to_str(set(set_one) & set(set_three) - set(set_two))
                )
            if venn_obj.get_label_by_id('011'):
                venn_obj.get_label_by_id('011').set_text(
                    SetsAlgorithm.set_to_str(set(set_two) & set(set_three) - set(set_one))
                )
            if venn_obj.get_label_by_id('111'):
                venn_obj.get_label_by_id('111').set_text(
                    SetsAlgorithm.set_to_str(set(set_one) & set(set_two) & set(set_three))
                )
        elif self.num_sets == 2:
            set_one = SetsAlgorithm.safe_eval(self.sets[0])
            set_two = SetsAlgorithm.safe_eval(self.sets[1])
            subsets = {
                '10': len(set(set_one) - set(set_two)),
                '01': len(set(set_two) - set(set_one)),
                '11': len(set(set_one) & set(set_two))
            }
            venn_obj = venn2(subsets=subsets, set_labels=(self.set_names[0], self.set_names[1]))
            if venn_obj.get_label_by_id('10'):
                venn_obj.get_label_by_id('10').set_text(
                    SetsAlgorithm.set_to_str(set(set_one) - set(set_two))
                )
            if venn_obj.get_label_by_id('01'):
                venn_obj.get_label_by_id('01').set_text(
                    SetsAlgorithm.set_to_str(set(set_two) - set(set_one))
                )
            if venn_obj.get_label_by_id('11'):
                venn_obj.get_label_by_id('11').set_text(
                    SetsAlgorithm.set_to_str(set(set_one) & set(set_two))
                )
        else:
            return


        plt.show()

    def draw_venn_4_more(self):
        """
        رسم نمودار ون برای 4 یا چند مجموعه درون یک فریم Tkinter.
        این تابع نمودار را داخل parent_frame قرار می‌دهد.
        """
        # تنظیم اندازه شکل با ارتفاع کمتر
        fig = plt.figure(figsize=(10, 5))
        ax = fig.add_subplot(111)

        # آماده‌سازی داده‌های نمودار ون با تغییر نام به "مجموعه X"
        venn_data = {}
        for i in range(self.num_sets):
            name = self.set_names[i]
            if name.startswith("Set "):
                name = name.replace("Set ", "مجموعه ")
            # تبدیل مقدار به set به صورت صریح
            venn_data[name] = SetsAlgorithm.safe_eval(self.sets[i])
        print(venn_data)
        print(type(venn_data))
        venn_data = {k: set(v) for k, v in venn_data.items()}

        # رسم نمودار ون روی محور مشخص (ax)
        # توجه: اگر تابع venn.venn از پارامتر ax پشتیبانی نکند،
        # ممکن است نیاز به تغییرات جزئی داشته باشید یا از یک کتابخانه‌ی متفاوت استفاده کنید.
        venn.venn(venn_data, ax=ax)
        
        # ذخیره نمودار در صورت وجود مسیر خروجی
        fig.show()


    @staticmethod
    def safe_eval(s):

        if isinstance(s, (set, frozenset)):
            return frozenset(s)
        return eval(s if isinstance(s, str) else repr(s), {"__builtins__": {}, "frozenset": frozenset})

    def get_region_info(self):
        """
        محاسبه اطلاعات نواحی نمودار ون:
        - برای هر ترکیب از مجموعه‌ها، ناحیه مربوطه محاسبه می‌شود.
        - نواحی دارای محتوا، به همراه نمادگذاری مناسب برگردانده می‌شوند.
        """
        result = {}
        sets_names = self.set_names
        sets_dict = self.set_of_sets
        n = self.num_sets

        for r in range(1, n + 1):
            for include in combinations(range(n), r):
                included_sets = [sets_names[i] for i in include]
                excluded_sets = [sets_names[i] for i in range(n) if i not in include]

                region = frozenset.intersection(*[SetsAlgorithm.safe_eval(sets_dict[name]) for name in included_sets])
                for name in excluded_sets:
                    region = region - SetsAlgorithm.safe_eval(sets_dict[name])
                if region:
                    if len(included_sets) > 1:
                        inc_notation = '(' + '∩'.join(included_sets) + ')'
                    else:
                        inc_notation = included_sets[0]
                    if excluded_sets:
                        if len(excluded_sets) > 1:
                            exc_notation = '(' + '∪'.join(excluded_sets) + ')'
                        else:
                            exc_notation = excluded_sets[0]
                        notation = inc_notation + '-' + exc_notation
                    else:
                        notation = inc_notation
                    result[notation] = region
        return result


class App:
    def __init__(self):
        st.set_page_config(
            layout="wide", 
            page_title="راهنمای ریاضی", 
            page_icon="🧮",
            initial_sidebar_state="expanded"
        )
        
        # خواندن و تبدیل فونت به Base64
        with open("data/font/FarhangVariable.woff", "rb") as font_file:
            encoded_font = base64.b64encode(font_file.read()).decode('utf-8')

        # اعمال CSS برای فونت و استایل‌های عمومی
        st.markdown(
            f"""
            <style>
            @font-face {{
                font-family: 'Farhang';
                src: url(data:font/woff;base64,{encoded_font}) format('woff');
                font-display: fallback;
            }}
            /* تنظیم فونت برای تمام عنوان‌ها */
            .st-emotion-cache-1p9ibxm h1, .st-emotion-cache-1p9ibxm h2, .st-emotion-cache-1p9ibxm h3, .st-emotion-cache-1p9ibxm h4, .st-emotion-cache-1p9ibxm h5, .st-emotion-cache-1p9ibxm h6, .st-emotion-cache-1p9ibxm span {{
                font-family:"Farhang";
                font-weight:200;
            }}
            .st-emotion-cache-3gzemd h1, .st-emotion-cache-3gzemd h2, .st-emotion-cache-3gzemd h3, .st-emotion-cache-3gzemd h4, .st-emotion-cache-3gzemd h5, .st-emotion-cache-3gzemd h6{{
                font-family:"Farhang"; 
                font-weight:200;           
            }}
            html, body, [class*="st-"] {{            
                font-family: 'Farhang' !important;
                font-size:22px;
            }}
            .stMain {{
                direction: rtl !important;

            }}

            section[data-testid="stSidebar"] {{
                direction: rtl;
            }}
            .stCheckbox {{
                display: flex;
                justify-content: center;
            }}
            [data-testid="stHeaderActionElements"]{{
                display:none;
            }}

            .st-emotion-cache-1jtnsb8 {{
                min-width: 400px;
                max-width: 450px;
            }}
            .stCheckbox {{
                direction: ltr !important;
            }}

            .stSidebar > .stCheckbox > label {{
                text-align: center !important;
            }}
            div.stButton>[disabled] {{
                color: #767b81 !important;
                background-color: #aec5dc !important;
            }}
            div.stButton > button {{
                background-color: rgb(13, 110, 253) !important;
                color: white !important;
                border-radius: 100px !important;
                border: none !important;
                cursor: pointer !important;
                transition: 0.5s ease-in-out, transform 0.2s !important;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important;
                background-image: linear-gradient(180deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0)) !important;
            }}
            div.stButton>[class*="st-"] {{
                padding:0 ;
            }}
            div.stButton > button p {{
                font-size: 19px !important;
                font-weight: 200 !important;    
            }}
            .dataframe th {{
            font-size: 18px !important;
            }}
            .dataframe td {{
            font-size: 18px !important;
            text-align: center !important;
            }}
            /* مخفی کردن سه‌نقطه‌ها در هدرهای DataFrame */
            .st-emotion-cache-1czn7q6  {{
                display: none !important;
            }}
            .st-emotion-cache-1wqrzgl {{
                min-width: 400px !important;
            }}
            [data-testid="stCheckbox"] [data-testid="stWidgetLabel"] p {{
                font-size: 20px !important;
            }}
            div.stButton > button:hover {{
                background: rgb(17, 72, 151) !important;
                transform: scale(1.05) !important;
            }}
            [data-baseweb="input"] {{
                font-family: 'Farhang', sans-serif !important;
                height: max-content !important;
                direction: ltr !important;
            }}
            .stTextInput > [data-testid="stWidgetLabel"] p {{
                font-size: 17px !important;
            }}
            input {{
                font-size: 23px !important;
            }}
            div.stButton > button:active {{
                background: rgb(38, 63, 100) !important;
                transform: scale(0.95) !important;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2) !important;
                color: white !important;
            }}
            </style>
            """, unsafe_allow_html=True
        )

        # مقداردهی اولیه session_state
        if "current_section" not in st.session_state:
            st.session_state["current_section"] = "sets"
        if "num_sets" not in st.session_state:
            st.session_state["num_sets"] = 1
        if "show_advanced" not in st.session_state:
            st.session_state["show_advanced"] = False
        if "show_hr_sidebar" not in st.session_state:
            st.session_state["show_hr_sidebar"] = False
        if "disabled_advanced_btn" not in st.session_state:
            st.session_state["disabled_advanced_btn"] = False
        if "disabled_next_set_btn" not in st.session_state:
            st.session_state["disabled_next_set_btn"] = False
        if "sets_data" not in st.session_state:
            st.session_state["sets_data"] = []
        self.main_menu()

    def main_menu(self):
        st.sidebar.markdown("<h1 style='color: #ff0000;  text-align:center;'>مجموعه‌ها</h1>", unsafe_allow_html=True)
        
        # منوی اصلی در سایدبار
        with st.sidebar.container():
            col1, col2 = st.sidebar.columns([1, 1])
            with col1:
                if st.button("مجموعه‌ها", use_container_width=True):
                    st.session_state["current_section"] = "sets"
                    st.session_state["show_hr_sidebar"] = False
            with col2:
                if st.button("خط", use_container_width=True):
                    st.session_state["current_section"] = "lines"
                    st.session_state["show_hr_sidebar"] = True

        if st.sidebar.button("گفتگو با هوش مصنوعی", use_container_width=True):
            st.session_state["current_section"] = "chatbot"
            st.session_state["show_hr_sidebar"] = True

        if st.session_state["show_hr_sidebar"]:
            st.sidebar.markdown("<hr>", unsafe_allow_html=True)

        # منوهای دیگر در سایدبار
        st.sidebar.markdown("<hr>", unsafe_allow_html=True)
        with st.sidebar.container():
            col1, col2 = st.sidebar.columns([1, 1])
            with col1:
                if st.button("درباره ما", use_container_width=True):
                    st.session_state["current_section"] = "about"
            with col2:
                if st.button("نحوه کار در این بخش", use_container_width=True):
                    st.session_state["current_section"] = "how_to_use"

        # نمایش بخش انتخاب‌شده
        if st.session_state["current_section"] == "sets":
            self.sets_section()
        elif st.session_state["current_section"] == "lines":
            self.show_lines_section()
        elif st.session_state["current_section"] == "chatbot":
            self.show_chatbot_section()
        elif st.session_state["current_section"] == "about":
            self.about_us()
        elif st.session_state["current_section"] == "how_to_use":
            self.how_to_use()
    def sets_section(self):
        st.markdown("<h1 style='color: #ff0000; text-align:center;'>مجموعه‌ها</h1>", unsafe_allow_html=True)

        # دکمه‌ی تغییر حالت پیشرفته
        st.toggle("حالت پیشرفته", key="show_advanced", on_change=self.on_advanced_toggle, disabled=st.session_state["disabled_advanced_btn"])

        # دریافت ورودی نام و مقدار مجموعه
        self.name_set = st.text_input(f"نام مجموعه {st.session_state['num_sets']} را وارد کنید:", max_chars=1)
        self.set_input = st.text_input(f"مجموعه {st.session_state['num_sets']} را وارد کنید:", key="set_input")

        # نمایش جدول مجموعه‌های ثبت‌شده
        self.display_table()

        # دکمه‌های کنترلی
        col1, col2, col3 = st.columns(3)
        with col3:
            st.button("پردازش مجموعه‌ها", use_container_width=True, on_click=self.display_sets)
        with col1:
            st.button("ثبت اطلاعات", key="add_set", use_container_width=True, on_click=self.next_set, disabled=st.session_state["disabled_next_set_btn"])
        with col2:
            st.button("مجموعه قبلی", use_container_width=True, on_click=self.previous_set)

    def on_advanced_toggle(self):
        if st.session_state["show_advanced"] and st.session_state["num_sets"] < 6:
            st.session_state["disabled_next_set_btn"] = False
        elif not st.session_state["show_advanced"] and st.session_state["num_sets"] > 3:
            st.session_state["disabled_next_set_btn"] = True

    def show_lines_section(self):
        st.markdown("<h1 style='color: #007bff; text-align:center;'>بخش خطوط</h1>", unsafe_allow_html=True)
        st.write("اینجا اطلاعات مربوط به خطوط نمایش داده می‌شود.")

    def show_chatbot_section(self):
        st.markdown("<h1 style='color: #28a745; text-align:center;'>گفتگو با هوش مصنوعی</h1>", unsafe_allow_html=True)
        st.write("اینجا گفتگو با هوش مصنوعی انجام می‌شود.")

    def about_us(self):
        st.markdown("<h1 style='color: #ff8000; text-align:center;'>درباره ما</h1>", unsafe_allow_html=True)
        st.write("اینجا اطلاعات درباره تیم و پروژه آورده می‌شود.")

    def how_to_use(self):
        st.markdown("<h1 style='color: #ff00ff; text-align:center;'>نحوه استفاده</h1>", unsafe_allow_html=True)
        st.write("اینجا نحوه استفاده از برنامه توضیح داده می‌شود.")
    def next_set(self):
        if not self.check_sets_input():
            return
        
        # اضافه کردن مجموعه جدید به لیست و افزایش شماره مجموعه
        st.session_state["sets_data"].append({"نام مجموعه": self.name_set, "مقدار مجموعه": self.set_input})
        st.session_state["num_sets"] += 1

        # کنترل تعداد مجموعه‌ها در حالت‌های مختلف
        if not st.session_state["show_advanced"] and st.session_state["num_sets"] == 3:
            with st.container():
                st.session_state["disabled_next_set_btn"] = True
                st.info("این مجموعه در حالت عادی آخرین مجموعه است.")
        elif st.session_state["show_advanced"] and st.session_state["num_sets"] == 6:
            with st.container():
                st.session_state["disabled_next_set_btn"] = True
                st.info("این مجموعه در حالت پیشرفته آخرین مجموعه است.")
        elif st.session_state["show_advanced"] and st.session_state["num_sets"] == 4:
            self.advanced_dialog()
    def previous_set(self):
        if st.session_state["sets_data"]:
            st.session_state["sets_data"].pop()  # حذف آخرین مجموعه ثبت‌شده
            st.session_state["num_sets"] -= 1 
    def display_table(self):
        """نمایش جدول با اسکرول و بدون منوی سه‌نقطه‌ای"""
        if st.session_state["sets_data"]:
            df = pd.DataFrame(st.session_state["sets_data"])
            st.data_editor(df, hide_index=True, use_container_width=True, height=200, disabled=True)
    def check_sets_input(self):
        # حذف فاصله‌های اضافی از ورودی مجموعه
        self.set_input = self.set_input.replace(" ", "")

        if not self.name_set:
            App.error_modal("نام مجموعه را وارد کنید!")
            return False
            
        elif not re.fullmatch(r"[A-Za-z]+", self.name_set.strip()):
            App.error_modal("نام مجموعه باید فقط شامل حروف انگلیسی باشد!")
            return False
            
        elif not self.set_input:
            App.error_modal("مجموعه را وارد کنید!")
            return False

        elif self.set_input.count("{") != self.set_input.count("}"):
            App.error_modal("تعداد اکلاد های باز و بسته برابر نیست!")
            return False

        elif not (self.set_input.startswith("{") and self.set_input.endswith("}")):
            App.error_modal("مجموعه باید با اکلاد باز و بسته شود!")
            return False
            
        if self.name_set.islower():
            self.error_modal(message="مجموعه به صورت کوچک نوشته شده است. به صورت خودکار به بزرگ تبدیل می‌شود.",typer="info")
            self.name_set = self.name_set.strip().upper()
            return True
        else:
            try:
                transformed = SetsAlgorithm.parse_set_string(SetsAlgorithm.fix_set_variables(self.set_input))
                eval_set = eval(transformed, {"__builtins__": {}, "frozenset": frozenset})
            except Exception as e:
                if self.set_input == "{}":
                    App.error_modal("مجموعه نمی‌تواند خالی باشد!")
                else:   
                    App.error_modal(f"خطا در تبدیل مجموعه: {e}")
                return False
        return True

    def previous_set(self):
        if st.session_state["num_sets"] > 1:
            st.session_state["num_sets"] -= 1

    def display_sets(self):
        st.write("مجموعه‌ها پردازش شدند!")

    # متد مربوط به نمایش مودال حالت پیشرفته (همانند نمونه داکیومنت)
    @staticmethod
    @st.dialog("حالت پیشرفته دائمی")
    def advanced_dialog():
        st.write("حالت پیشرفته به صورت دائمی فعال خواهد شد. آیا ادامه می‌دهید؟")
        col1,col2=st.columns(2)
        with col1:
            if st.button("بله", key="advanced_yes",use_container_width=True):
                st.session_state["show_advanced"] = True
                st.session_state["disabled_advanced_btn"] = True
                st.rerun()
        with col2:
            if st.button("خیر", key="advanced_no",use_container_width=True):
                st.session_state["num_sets"] -= 1
                st.rerun()
    def previous_set(self):
        if st.session_state["num_sets"] > 1:
            st.session_state["num_sets"] -= 1

    # متد استاتیک برای نمایش مودال خطا
    @staticmethod
    @st.dialog("خطا")
    def error_modal(message,typer="error"):
        if typer=="error":
            st.error(message)
        else:
            st.info(message)
        if st.button("اوکی", key="error_ok",use_container_width=True):
            st.rerun()


# اجرای اپلیکیشن
App()
