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
from io import BytesIO


# --------------------------------------------------
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
        به‌طوری که اگر یک عنصر در عمق ۱ قرار داشته باشد و قبلاً در کوتیشن نباشد،
        آن را در کوتیشن قرار می‌دهد.
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
                    if fixed_token.isdigit():
                        fixed_token = str(int(fixed_token))
                    elif brace_level == 1 and fixed_token and not (fixed_token.startswith('"') and fixed_token.endswith('"')):
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
                    if fixed_token.isdigit():
                        fixed_token = str(int(fixed_token))
                    elif brace_level == 1 and fixed_token and not (fixed_token.startswith('"') and fixed_token.endswith('"')):
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
                    if fixed_token.isdigit():
                        fixed_token = str(int(fixed_token))
                    elif brace_level == 1 and fixed_token and not (fixed_token.startswith('"') and fixed_token.endswith('"')):
                        fixed_token = f'"{fixed_token}"'
                    result.append(fixed_token)
                    token = ""
                else:
                    # اگر توکن خالی است و کاراکتر مورد نظر غیر از کاما است و در عمق ۱ قرار دارد،
                    # آن را به عنوان یک عنصر (رشته) در کوتیشن قرار می‌دهیم.
                    if ch != ',' and brace_level == 1:
                        result.append(f'"{ch}"')
                    else:
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
            if fixed_token.isdigit():
                fixed_token = str(int(fixed_token))
            elif brace_level == 1 and fixed_token and not (fixed_token.startswith('"') and fixed_token.endswith('"')):
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
            subsets_dict = {f"زیرمجموعه {i} عضوی": [] for i in range(11)}
        else:
            subsets_dict = {f"زیرمجموعه {i} عضوی": [] for i in range(len(given_set)+1)}
        for i in range(len(given_set) + 1):
            if num_loop > 10:
                break
            for subset in combinations(given_set, i):
                # تبدیل tuple به رشته با آکولاد
                subset_str = "{" + ", ".join(map(str, subset)) + "}"
                subsets_dict[f"زیرمجموعه {i} عضوی"].append(subset_str)
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
    @staticmethod
    def partitions_to_str(given_set):
        """
        تبدیل افرازهای مجموعه به رشته:
        - برای هر افراز (که شامل چند زیرمجموعه است)، هر زیرمجموعه به صورت {a, b, ...} نمایش داده می‌شود.
        - زیرمجموعه‌ها با " | " از هم جدا می‌شوند.
        """
        # ابتدا افرازهای مجموعه را محاسبه می‌کنیم
        partitions = SetsAlgorithm.partitions(given_set)
        partitions_str = []
        for partition in partitions:
            # هر partition یک لیست از زیرمجموعه‌ها (tupleها) است.
            subset_strs = []
            for subset in partition:
                # تبدیل tuple به رشته با آکولاد
                subset_str = "{" + ", ".join(map(str, subset)) + "}"
                subset_strs.append(subset_str)
            # اتصال زیرمجموعه‌ها با جداکننده
            partitions_str.append(" | ".join(subset_strs))
        return partitions_str
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



    def check_variable_depths(self, expression: str) -> dict:
        """
        بررسی عمق هر متغیر در عبارت.
        متغیرهایی که در بخش‌های کوتیشن قرار دارند، نادیده گرفته می‌شوند.
        این تابع یک دیکشنری برمی‌گرداند که کلید آن نام متغیر و مقدار آن لیستی از عمق‌های حضور آن در عبارت است.
        """
        depths = {}
        current_depth = 0
        i = 0
        while i < len(expression):
            ch = expression[i]
            if ch == '"':
                # گذر از بخش‌های کوتیشن‌دار
                i += 1
                while i < len(expression) and expression[i] != '"':
                    i += 1
                i += 1  # گذر از کوتیشن پایانی
                continue
            elif ch == '{':
                current_depth += 1
                i += 1
                continue
            elif ch == '}':
                current_depth -= 1
                i += 1
                continue
            elif ch.isalpha() or ch == '_':
                start = i
                while i < len(expression) and (expression[i].isalnum() or expression[i] == '_'):
                    i += 1
                token = expression[start:i]
                # ثبت عمق متغیر
                if token not in depths:
                    depths[token] = []
                depths[token].append(current_depth)
                continue
            else:
                i += 1
        return depths

    def U_I_Ms_advance(self, text: str) -> str:
        """
        محاسبه ادونس با بررسی عمق متغیرهای موجود در عبارت.
        در این تابع:
        - ابتدا علائم ∩ و ∪ به معادل‌های Python تبدیل می‌شوند.
        - متغیرهای داخل مجموعه‌ها با استفاده از fix_set_variables اصلاح می‌شوند.
        - عمق هر متغیر در عبارت محاسبه می‌شود. اگر متغیری یا در هیچ عمقی (یعنی خارج از {}) ظاهر شده باشد یا تعریف نشده باشد، خطا داده می‌شود.
        - در نهایت عبارت پردازش و نتیجه بازگردانده می‌شود.
        """
        # جایگزینی علائم ∩ و ∪
        text = text.replace('∩', '&').replace('∪', '|')
        
        # اصلاح متغیرهای داخل مجموعه‌ها
        fixed_text = SetsAlgorithm.fix_set_variables(text)
        
        # بررسی عمق متغیرها
        var_depths = self.check_variable_depths(fixed_text)
        for var, depths in var_depths.items():
            # اگر متغیر تعریف نشده باشد
            if var.upper() not in self.set_of_sets:
                return f"متغیر '{var}' تعریف نشده است!"
            # اگر متغیر تنها در عمق 0 (خارج از مجموعه‌ها) ظاهر شده باشد
            if all(d == 0 for d in depths):
                if var.upper() not in self.set_of_sets:
                    return f"متغیر '{var}' تعریف نشده است!"
        
        # تبدیل عبارت به فرمت مناسب برای eval
        transformed_text = SetsAlgorithm.parse_set_string(fixed_text)
        
        # آماده‌سازی دیکشنری متغیرها (با توجه به اینکه ممکن است نام‌ها به حروف کوچک نیز مورد استفاده قرار گیرند)
        variables = {name: frozenset(set_val) for name, set_val in self.set_of_sets.items()}
        variables.update({name.lower(): frozenset(set_val) for name, set_val in self.set_of_sets.items()})
        
        try:
            result = eval(transformed_text, {"__builtins__": {}, "frozenset": frozenset}, variables)
            return self.set_to_str(result)
        except Exception as e:
            return f"خطا در ارزیابی عبارت:\n{e}"


    @staticmethod
    def set_to_str(result):
        """
        تبدیل نتیجه مجموعه به رشته:
        - خروجی در داخل آکولاد {} نمایش داده می‌شود.
        - اعضای مجموعه به صورت ساده (بدون کوتیشن) نمایش داده می‌شوند.
        """
        if isinstance(result, (set, frozenset)):
            def format_item(item):
                if isinstance(item, (set, frozenset)):
                    return SetsAlgorithm.set_to_str(item)
                elif isinstance(item, str):
                    # اگر رشته با " یا ' شروع و پایان یافته، آن‌ها را حذف کن
                    if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
                        return item[1:-1]
                    return item
                else:
                    return str(item)
            return "{" + ", ".join(format_item(item) for item in result) + "}"
        else:
            return str(result)

    def draw_venn(self):
        """
        رسم نمودار ون برای دو یا سه مجموعه.
        """
        fig, ax = plt.subplots()
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
            return None

        return fig

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
        return fig

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

# --------------------------------------------------


class App:
    def __init__(self):
        self.setup_page()
        self.initialize_session_state()
        self.main_menu()

    def setup_page(self):
        st.set_page_config(
            layout="wide",
            page_title="راهنمای ریاضی",
            page_icon="",
            initial_sidebar_state="expanded"
        )
        with open("data/img/bg.png", "rb") as f:
            bg = base64.b64encode(f.read()).decode("utf-8")
        with open("data/font/YekanBakhFaNum-Fat.woff2", "rb") as f:
            yekan_fat = base64.b64encode(f.read()).decode("utf-8")
        with open("data/font/YekanBakhFaNum-Bold.woff2", "rb") as f:
            yekan_bold = base64.b64encode(f.read()).decode("utf-8")
        with open("data/font/YekanBakhFaNum-Heavy.woff2", "rb") as f:
            yekan_heavy = base64.b64encode(f.read()).decode("utf-8")
        with open("data/font/YekanBakhFaNum-Light.woff2", "rb") as f:
            yekan_light = base64.b64encode(f.read()).decode("utf-8")
        with open("data/font/YekanBakhFaNum-Medium.woff2", "rb") as f:
            yekan_medium = base64.b64encode(f.read()).decode("utf-8")
        with open("data/font/YekanBakhFaNum-Regular.woff2", "rb") as f:
            yekan_regular = base64.b64encode(f.read()).decode("utf-8")

        st.markdown(f"""
        <style>
        @font-face {{
            font-family: 'YekanBakhFaNum';
            src: url(data:font/woff2;base64,{yekan_fat}) format('woff2');
            font-weight: 900;
            font-style: normal;
        }}
        @font-face {{
            font-family: 'YekanBakhFaNum';
            src: url(data:font/woff2;base64,{yekan_bold}) format('woff2');
            font-weight: bold;
            font-style: normal;
        }}
        @font-face {{
            font-family: 'YekanBakhFaNum';
            src: url(data:font/woff2;base64,{yekan_heavy}) format('woff2');
            font-weight: 800;
            font-style: normal;
        }}
        @font-face {{
            font-family: 'YekanBakhFaNum';
            src: url(data:font/woff2;base64,{yekan_light}) format('woff2');
            font-weight: 300;
            font-style: normal;
        }}
        @font-face {{
            font-family: 'YekanBakhFaNum';
            src: url(data:font/woff2;base64,{yekan_medium}) format('woff2');
            font-weight: 500;
            font-style: normal;
        }}
        @font-face {{
            font-family: 'YekanBakhFaNum';
            src: url(data:font/woff2;base64,{yekan_regular}) format('woff2');
            font-weight: normal;
            font-style: normal;
        }}


        </style>
        """, unsafe_allow_html=True)
        st.markdown(
            f"""
            <style>
            html, body, [class*="st-"] {{
            font-family: 'YekanBakhFaNum'!important;\
                font-size:22px !important;
            }}
            .stApp::before {{
                content: "";
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: url('data:image/png;base64,{bg}') no-repeat center center;
                background-size: cover;
                filter: blur(4px); 
            }}
            .stSidebar::before {{
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: url('data:image/png;base64,{bg}') no-repeat center center;
                background-size: cover;
                filter: blur(3px);
                z-index: -1;       
            }}
            .stExpander{{
                border-radius: 40px;
                background-color: #ffffffcc;
            }}  
            .stForm {{
            border-radius: 40px;
            background-color: #ffffffcc;
            }}
            .stExpander details{{
                border-radius: 40px;
            }}
            h1,h2,h3,h4,h5,h6,span
             {{
                font-family:'YekanBakhFaNum' !important;
                font-weight:300 !important;
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
            [data-testid="stHeaderActionElements"] {{
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
            [kind="secondaryFormSubmit"][disabled] {{
                color: #767b81 !important;
                background-color: #aec5dc !important;                
            }}
            [kind="secondaryFormSubmit"] {{
                background-color: rgb(13, 110, 253) !important;
                color: white !important;
                border-radius: 100px !important;
                border: none !important;
                cursor: pointer !important;
                transition: 0.5s ease-in-out, transform 0.2s !important;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important;
                background-image: linear-gradient(180deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0)) !important;
            }}
            div.stButton > button ,[data-testid="stBaseButton-secondary"]{{
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
                font-weight: 300 !important;
            }}
            div.stButton > button p ,[data-testid="stBaseButton-secondary"] p {{
                font-size: 19px !important;
                font-weight: 300 !important;
            }}
            [kind="secondaryFormSubmit"] p {{
                font-size: 19px !important;
                font-weight: 300 !important;
            }}
            .dataframe th {{
                font-size: 18px !important;
            }}
            .dataframe td {{
                font-size: 18px !important;
                text-align: center !important;
            }}
            .st-emotion-cache-1czn7q6 {{
                display: none !important;
            }}
            section[data-testid="stSidebar"] {{
                position: fixed !important;  /* ثابت روی صفحه */
                top: 0;
                left: 0;
                height: 100%;
                width: 300px; /* یا هر عرض مناسب */
                overflow-y: auto !important; /* اسکرول عمودی فعال */
                box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
                visibility: visible; 
            }}

            section[data-testid="stSidebar"] > div {{
                overflow-y: auto !important;
                max-height: 100vh !important;
            }}
            [data-testid="stSidebarCollapseButton"]{{
                display: inline-flex !important;
            }}
            @media (min-width: 1231px) {{
                section[data-testid="stSidebar"] {{
                    position: relative !important;
                    visibility:visible;

                }}
            }}

            .st-emotion-cache-1wqrzgl {{
                min-width: 400px !important;
            }}
            [data-testid="stCheckbox"] [data-testid="stWidgetLabel"] p {{
                font-size: 20px !important;
            }}
            @media (max-width:460px){{
                [role="dialog"]{{
                    min-width:100px
                }}
            }}
            @media (min-width:460px){{
                .stApp::before {{
                filter: blur(5px); 
                }}
            }}
                
            div.stButton > button:hover ,[data-testid="stBaseButton-secondary"]:hover{{
                background: rgb(17, 72, 151) !important;
                transform: scale(1.05) !important;
            }}
            .stSidebar[aria-expanded="true"] {{
                visibility:visible;
            }}
            [kind="secondaryFormSubmit"]:hover {{
                background: rgb(17, 72, 151) !important;
                transform: scale(1.05) !important;
            }}
            [data-baseweb="input"] {{
                font-family: 'YekanBakhFaNum'!important;
                height: max-content !important;
                direction: ltr !important;
            }}
            .stTextInput > [data-testid="stWidgetLabel"] p {{
                font-size: 17px !important;
            }}
            input {{
                font-size: 23px !important;
            }}
            div.stButton > button:active ,[data-testid="stBaseButton-secondary"]:active {{
                background: rgb(38, 63, 100) !important;
                transform: scale(0.95) !important;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2) !important;
                color: white !important;
            }}
            [kind="secondaryFormSubmit"]:active {{
                background: rgb(38, 63, 100) !important;
                transform: scale(0.95) !important;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2) !important;
                color: white !important;
            }}
            </style>
            """, unsafe_allow_html=True
        )


    def initialize_session_state(self):
        defaults = {
            "current_section": "sets",
            "num_sets": 1,
            "show_advanced": False,
            "show_hr_sidebar": False,
            "disabled_advanced_btn": False,
            "disabled_next_set_btn": False,
            "sets_data": [],
            "show_error_expander": False,
            "error_message": "",
            "error_type": "error",
            "confirm_prev": False,
            "pending_delete_confirm": False,
            "pending_delete_data": [],
            "advanced_quesion": False,
            "notifications": [],
            "confirm_delete_open": False,
            "confirm_delete_table":False,
            "calc_result":"در انتظار عبارت",
            "venn_fig":None,
            "hide_sets_btn":True
        }
        for key, val in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = val

    def add_notification(self, message, error_type="error"):
        st.session_state["notifications"].append({
            "message": message,
            "error_type": error_type
        })

    def render_notification(self,frame):
        with frame.container():
            if st.session_state["notifications"]:
                for index, noti in enumerate(st.session_state["notifications"][:]):
                    with st.expander("خطا" if noti["error_type"]=="error" else "اطلاع", expanded=True):
                        if noti["error_type"] == "error":
                            st.error(noti["message"])
                        else:
                            st.info(noti["message"])
                        if st.button("اوکی", key=f"okey {index}", use_container_width=True):
                            st.session_state["error_message"] = ""
                            st.session_state["show_error_expander"] = False
                            st.session_state["notifications"]=[]
                            st.rerun()


    def main_menu(self):
        st.sidebar.markdown("<h1 style='color: #ff0000; text-align:center;'>منو اصلی</h1>", unsafe_allow_html=True)
        col1, col2 = st.sidebar.columns([1, 1])



        with col1:
            if st.button("مجموعه‌ها", use_container_width=True):
                st.session_state["current_section"] = "sets"
                st.session_state["show_hr_sidebar"] = False
                defaults = {
                "show_advanced": False,
                "disabled_advanced_btn": False,
                "disabled_next_set_btn": False,
                "sets_data": [],
                "show_error_expander": False,
                "error_message": "",
                "error_type": "error",
                "confirm_prev": False,
                "num_sets": 1,
                "pending_delete_confirm": False,
                "pending_delete_data": [],
                "advanced_quesion": False,
                "notifications": [],
                "confirm_delete_open": False,
                "confirm_delete_table":False,
                "venn_fig":None,
                "hide_sets_btn":True

                }
                for key, val in defaults.items():
                    st.session_state[key] = val
        with col2:
            if st.button("خط", use_container_width=True):
                st.session_state["current_section"] = "lines"
                st.session_state["show_hr_sidebar"] = True

        if st.sidebar.button("گفتگو با هوش مصنوعی", use_container_width=True):
            st.session_state["current_section"] = "chatbot"
            st.session_state["show_hr_sidebar"] = True

        if st.session_state["show_hr_sidebar"]:
            st.sidebar.markdown("<hr>", unsafe_allow_html=True)
            self.more_opition=st.sidebar.empty()
        st.sidebar.markdown("<hr>", unsafe_allow_html=True)
        col1, col2 = st.sidebar.columns([1, 1])
        with col1:
            if st.button("درباره ما", use_container_width=True):
                st.session_state["current_section"] = "about"
        with col2:
            if st.button("نحوه کار در این بخش", use_container_width=True):
                st.session_state["current_section"] = "how_to_use"

        section = st.session_state["current_section"]
        self.body=st.empty()
        if section == "sets":
            self.body.empty()
            with self.body.container():
                self.initialize_session_state()
                self.sets_section()
        elif section == "lines":
            self.body.empty()
            with self.body.container():
                self.show_lines_section()
        elif section == "chatbot":
            self.body.empty()
            with self.body.container():
                self.show_chatbot_section()
        elif section == "about":
            self.body.empty()
            with self.body.container():
                self.about_us()
        elif section == "how_to_use":
            self.body.empty()
            with self.body.container():
                self.how_to_use()
        elif section == "display_sets":
            self.body.empty()
            with self.body.container():
                self.display_sets()

    def sets_section(self):

        st.markdown("<h1 style='color: #ff0000; text-align:center;'>مجموعه‌ها</h1>", unsafe_allow_html=True)
        st.toggle("حالت پیشرفته", key="show_advanced", on_change=self.on_advanced_toggle,
                  disabled=st.session_state["disabled_advanced_btn"])
        self.notification_placeholder = st.empty()

        with st.form(key="sets_form",  enter_to_submit=False):
            self.name_set = st.text_input(f"نام مجموعه {st.session_state['num_sets']} را وارد کنید:", max_chars=1,help="فقط از نام انگلسی و تک حرفی استفاده نماید")
            self.set_input = st.text_input(f"مجموعه {st.session_state['num_sets']} را وارد کنید:", key="set_input",help="  تعداد اکلاد ها های باز و بسته برابر باشند و حتما مجموعه با اکلاد باز و بسته شود و در حال حاظر از مجموعه تهی پشتیبانی نمیشود")
            with st.container():
                self.display_table()
            col1, col2,  = st.columns(2)
            next_btn = col1.form_submit_button("ثبت اطلاعات", use_container_width=True,
                                            disabled=st.session_state["disabled_next_set_btn"],help="با این کار اطلاعات ورودی ها ثبت و  به صفحه مجموعه بعدی می روید")
            end_btn = col2.form_submit_button("پردازش مجموعه ها های وارد شد",use_container_width=True,help="با این کار مجموعه هایی که تا الان وارد کردید پردازش میشود",disabled=st.session_state["hide_sets_btn"])
            prev_btn =col2.form_submit_button("مجموعه قبلی", use_container_width=True, on_click=self.previous_set,help="با این کار اطلعات مجموعه قبلی پاک و دوباره دریافت میشود",disabled=st.session_state["hide_sets_btn"])
            reg_end_btn =col1.form_submit_button(f"ثبت مجموعه {st.session_state["num_sets"]} و پردازش مجموعه‌ها", use_container_width=True,help="با این کار اطلاعات مجموعه فعلی ثبت و به صفحه پردازش می روید")
        if next_btn:
            self.next_set()
        if reg_end_btn:
            if not self.check_sets_input(end=True):
                pass
            else:
                st.session_state["sets_data"].append({
                    "نام مجموعه": self.name_set.upper(),
                    "مقدار مجموعه": self.set_input
                })
                if not st.session_state["num_sets"]==1:
                    st.session_state["show_hr_sidebar"] = True
                st.session_state["calc_result"]="در انتظار دریافت عبارت"
                st.session_state["current_section"] = "display_sets"  # یک مقدار جدید برای نمایش نتایج
                st.rerun()
        if end_btn:
            if not st.session_state["num_sets"]==1:
                st.session_state["show_hr_sidebar"] = True
            st.session_state["calc_result"]="در انتظار دریافت عبارت"
            st.session_state["current_section"] = "display_sets"  # یک مقدار جدید برای نمایش نتایج
            st.rerun()
        self.render_notification(self.notification_placeholder)

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
        self._yes_no_erorr = True
        if not self.check_sets_input():
            return

        if not st.session_state["show_advanced"] and st.session_state["num_sets"] == 2:
            st.session_state["sets_data"].append({
                "نام مجموعه": self.name_set.upper(),
                "مقدار مجموعه": self.set_input
            })
            st.session_state["num_sets"] += 1
            st.session_state["disabled_next_set_btn"] = True
            self.add_notification("این مجموعه در حالت عادی آخرین مجموعه است.", "info")
            return
        if st.session_state["num_sets"] == 3:
            self._yes_no_erorr=False
            if "advanced_confirmed" not in st.session_state:
                with self.notification_placeholder.container():
                    with st.expander("اطلاع" , expanded=True):
                        if self.name_set.upper()!=self.name_set:
                            st.info("نام مجموعه کوچک  بود و به طور خودکار بزرگ شد")
                    with st.expander("تایید", expanded=True):
                        st.info("حالت دائمی پیشرفته فعال خواهد شد")
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            def confirm_advanced():
                                st.session_state.disabled_advanced_btn = True
                                st.session_state["sets_data"].append({
                                    "نام مجموعه": self.name_set.upper(),
                                    "مقدار مجموعه": self.set_input
                                })
                                st.session_state["num_sets"] += 1
                            if st.button("بله", key="advanced_yes", use_container_width=True, on_click=confirm_advanced):
                                pass
                        with col2:
                            def cancel_advanced():
                                pass
                            if st.button("خیر", key="advanced_no", use_container_width=True, on_click=cancel_advanced):
                                pass
                return
        if st.session_state["show_advanced"] and st.session_state["num_sets"] == 5:
            st.session_state["sets_data"].append({
                "نام مجموعه": self.name_set.upper(),
                "مقدار مجموعه": self.set_input
            })
            st.session_state["num_sets"] += 1
            st.session_state["disabled_next_set_btn"] = True
            self.add_notification("این مجموعه در حالت پیشرفته آخرین مجموعه است.", "info")
            return

        st.session_state["sets_data"].append({
            "نام مجموعه": self.name_set.upper(),
            "مقدار مجموعه": self.set_input
        })
        st.session_state["hide_sets_btn"]=False
        st.session_state["num_sets"] += 1
        if self._yes_no_erorr:
            st.rerun()
    def previous_set(self):
        if st.session_state["sets_data"]:
            if "delete_confirmed" not in st.session_state:
                with self.notification_placeholder.container():
                    with st.expander("تایید", expanded=True):
                        st.info("مجموعه قبلی را حذف میکنیم ایا مطمئن هستید")
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            def confirm_delete():
                                st.session_state["sets_data"].pop()
                                st.session_state["num_sets"] = len(st.session_state["sets_data"]) + 1
                                st.session_state["disabled_next_set_btn"] = False
                                if st.session_state["num_sets"] < 4:
                                    st.session_state["disabled_advanced_btn"] = False
                                if st.session_state["num_sets"]==1:
                                    st.session_state["hide_sets_btn"]=True
                            if st.button("بله", key="confirm_yes", use_container_width=True, on_click=confirm_delete):
                                pass
                        with col2:
                            def cancel_delete():
                                pass
                            if st.button("خیر", key="confirm_no", use_container_width=True, on_click=cancel_delete):
                                pass



    def display_table(self):
        if st.session_state["sets_data"]:
            self.df = pd.DataFrame(st.session_state["sets_data"])

            self.edited_df = st.data_editor(
                self.df,
                num_rows="fixed",
                use_container_width=True,
                height=200,
                column_config={
                    "نام مجموعه": st.column_config.TextColumn("نام مجموعه", disabled=True),
                    "مقدار مجموعه": st.column_config.TextColumn("مقدار مجموعه", disabled=True)
                },
                hide_index=True
            )

    def check_sets_input(self,end=False):
        self.set_input = self.set_input.replace(" ", "")
        if not self.name_set:
            self.add_notification("نام مجموعه را وارد کنید!")
            return False
        elif not re.fullmatch(r"[A-Za-z]+", self.name_set.strip()):
            self.add_notification("نام مجموعه باید فقط شامل حروف انگلیسی باشد!")
            return False
        elif not self.set_input:
            self.add_notification("مجموعه را وارد کنید!")
            return False
        elif self.set_input.count("{") != self.set_input.count("}"):
            self.add_notification("تعداد اکلاد های باز و بسته برابر نیست!")
            return False
        elif not (self.set_input.startswith("{") and self.set_input.endswith("}")):
            self.add_notification("مجموعه باید با اکلاد باز و بسته شود!")
            return False
        else:
            try:
                transformed = SetsAlgorithm.parse_set_string(SetsAlgorithm.fix_set_variables(self.set_input))
                eval_set = eval(transformed, {"__builtins__": {}, "frozenset": frozenset})
            except Exception as e:
                if self.set_input == "{}":
                    self.add_notification("مجموعه نمی‌تواند خالی باشد!")
                else:
                    self.add_notification(f"خطا در تبدیل مجموعه: {e}")
                return False
        for dict_item in st.session_state["sets_data"]:
            if self.name_set.upper() == dict_item["نام مجموعه"]:
                self.add_notification("نام مجموعه تکراری است")
                return False
        if st.session_state["num_sets"] != 3 and self.name_set.islower():
            self.old_name_set=self.name_set
            if not end:
                self.add_notification("مجموعه به صورت کوچک نوشته شده است. به صورت خودکار به بزرگ تبدیل می‌شود.", "info")
            self.name_set = self.name_set.strip().upper()
            return True
        self._yes_no_erorr=True
        return True

    def on_advanced_toggle(self):
        if st.session_state["show_advanced"] and st.session_state["num_sets"] <= 6:
            st.session_state["disabled_next_set_btn"] = False
        elif not st.session_state["show_advanced"] and st.session_state["num_sets"] >= 3:
            st.session_state["disabled_next_set_btn"] = True

    def display_sets(self):
        st.toggle("حالت پیشرفته", key="show_advanced",disabled=True)
        self.notification_frame=st.empty()
        st.divider()
        set_of_sets={}
        for dic in st.session_state["sets_data"]:
            set_of_sets[dic["نام مجموعه"]] = eval(SetsAlgorithm.parse_set_string(SetsAlgorithm.fix_set_variables(str(dic["مقدار مجموعه"]))), {"__builtins__": {}, "frozenset": frozenset})
            if  st.session_state["num_sets"]==1:
                self.selected_option=dic["نام مجموعه"]
        self.sets=SetsAlgorithm(set_of_sets)
        menu_options = list(set_of_sets.keys()) + ["محاسبات"]
        if not st.session_state["num_sets"]==1:
            self.selected_option = self.more_opition.selectbox("انتخاب مجموعه یا بخش", menu_options)
        if self.selected_option in set_of_sets:
            selected_set=set_of_sets[self.selected_option]
            transformed = SetsAlgorithm.parse_set_string(SetsAlgorithm.fix_set_variables(str(selected_set)))
            evaluated = eval(transformed, {"__builtins__": {}, "frozenset": frozenset})
            set_obj = SetsAlgorithm.to_frozenset(evaluated)
            col1,col2,col3=st.columns([2,3,1])
            col1.write(f"نام مجموعه : {self.selected_option}")
            col2.write(f"اعضای مجموعه : {SetsAlgorithm.set_to_str(set_obj)}",unsafe_allow_html=True)
            col3.write(f"تعداد اعضای مجموعه : {len(selected_set)}")
            st.divider()
            col1,col2=st.columns([1,1])
            subsets = SetsAlgorithm.subsets_one_set(selected_set)

            # لیست برای نگهداری داده‌های جدول
            subset_list = []
            for key, value in subsets.items():
                for item in value:
                    subset_list.append((key, item))  # (نوع زیرمجموعه، مقدار)

            # ایجاد DataFrame همراه با شماره‌گذاری
            df_subsets = pd.DataFrame({
                "شماره": range(1, len(subset_list) + 1),  # شماره‌گذاری
                "زیرمجموعه": [s[1] for s in subset_list],  # مقدار زیرمجموعه
                "نوع زیرمجموعه": [s[0] for s in subset_list]  # نام دسته زیرمجموعه (n عضوی)
            })
            with col1.expander("زیر مجموعه ها"):
            # نمایش در Streamlit
                st.dataframe(df_subsets,use_container_width=True,hide_index=True)

            part = SetsAlgorithm.partitions_to_str(selected_set)

            df_part = pd.DataFrame({
                "شماره": range(1, len(part) + 1),  
                "افراز": part  
            })
            with col2.expander("افراز ها"):
                st.dataframe(df_part,hide_index=True,use_container_width=True)
            if st.session_state["num_sets"]==1 and  st.session_state["show_advanced"]:
                with st.expander("محاسبه",expanded=True):
                    with st.form("clac_form",enter_to_submit=False):
                        self.calc_input=st.text_input("عبارت مورد نظر را وارد کنید",key="calc_input",help="شما میتوانید از نام مجموعه ها برای مختصر نویسی استفاده کنید اگر نام دیگری استفاده کنید با ارور مواجه خواید شد و برای اشتراک از & و برای اجتماع از | استفاده کنید")
                        col2,col1=st.columns(2)
                        submit_btn=col1.form_submit_button("محاسبه جواب",help="با زدن این دکمه جواب عبارت برای شما محاسبه می شود")
                        col2.write(f"<div style='display: flex;justify-content: center;'>{st.session_state["calc_result"]}</div>",unsafe_allow_html=True)
                    if submit_btn:
                        self.calc_sets()
                
        elif self.selected_option == "محاسبات":
            info = self.sets.check_other_information()   
            st.subheader("بررسی زنجیره‌ای بودن مجموعه‌ها")
            if info["all_sets_chain"]:
                st.success("همه مجموعه‌ها به صورت زنجیره‌ای مرتب هستند.")
            else:
                st.warning("مجموعه‌ها به صورت زنجیره‌ای مرتب نیستند.")
            with st.expander("بررسی نسبت مجموعه ها با هم دیگر"):             
                df_subsets_info = pd.DataFrame(info["subsets_info"]).T
                df_subsets_info.index = [name.replace("Set", "مجموعه").replace("set", "مجموعه") for name in df_subsets_info.index]
                df_subsets_info.columns = [col.replace("Set", "مجموعه").replace("set", "مجموعه") for col in df_subsets_info.columns]

                # اضافه کردن نام مجموعه‌های ردیف به یک ستون جدید به نام "مجموعه ردیف" و حذف index
                df_subsets_info.insert(0, "نام زیر مجموعه", df_subsets_info.index)
                df_subsets_info = df_subsets_info.reset_index(drop=True)

                # پردازش سلول‌ها:
                # - اگر مقدار True باشد: "✓"
                # - اگر مقدار False باشد: "✗"
                # - اگر ردیف و ستون یکسان باشند: "--"
                for i in range(len(df_subsets_info)):
                    for col in df_subsets_info.columns[1:]:  # از ستون دوم به بعد پردازش شود
                        if df_subsets_info.at[i, "نام زیر مجموعه"] == col:
                            df_subsets_info.at[i, col] = "---"
                        else:
                            if df_subsets_info.at[i, col]:
                                df_subsets_info.at[i, col] = "✓"
                            else:
                                df_subsets_info.at[i, col] = "✗"

                # نمایش جدول با تنظیمات بهتر
                st.dataframe(df_subsets_info, hide_index=True)

                # نمایش توضیح جداگانه در زیر جدول
                st.info(
                    "در جدول بالا:\n"
                    "✓ : نشان‌دهنده‌ی زیرمجموعه بودن مجموعه موجود در ردیف نسبت به مجموعه موجود در ستون است.\n"
                    "✗ : نشان‌دهنده‌ی عدم زیرمجموعه بودن است.\n"
                    "-- : همان مجموعه مورد نظر است"
                )
            st.divider()
            with st.expander("نمودار ون"):
                st.subheader("اطلاعات نواحی نمودار")
                region_info = self.sets.get_region_info()
                if region_info:
                    df_region = pd.DataFrame({
                        "ناحیه": list(region_info.keys()),
                        "مقدار": [SetsAlgorithm.set_to_str(v) for v in region_info.values()]
                    })
                    st.dataframe(df_region, hide_index=True)
                else:
                    st.info("هیچ ناحیه‌ای یافت نشد.")
                
                # دکمه رسم نمودار
                if st.button("رسم نمودار ون", key="venn_btn", use_container_width=True,help="با زدن این دکمه نمودار ون مجموعه ها رسم می شود"):
                    if st.session_state["show_advanced"] and len(set_of_sets)>3:
                        st.session_state.venn_fig = self.sets.draw_venn_4_more()
                    else:
                        st.session_state.venn_fig = self.sets.draw_venn()
                save_venn_btn_frame=st.empty()
                # نمایش نمودار اگر قبلاً ساخته شده باشد
                if not st.session_state["venn_fig"] is None :
                    st.pyplot(st.session_state.venn_fig, clear_figure=False)
                    
                    # ایجاد دکمه دانلود
                    buffer = BytesIO()
                    st.session_state.venn_fig.savefig(buffer, format="png")
                    buffer.seek(0)
                    save_venn_btn_frame.download_button(
                        label="دانلود نمودار ون",
                        data=buffer,
                        file_name="venn_diagram.png",
                        mime="image/png",
                        use_container_width=True,
                        help="با زدن این دکمه نمودار ون برای شما دانلود میشود"
                    )

            if  st.session_state["show_advanced"]:
                with st.expander("محاسبه",expanded=True):
                    with st.form("clac_form",enter_to_submit=False):
                        self.calc_input=st.text_input("عبارت مورد نظر را وارد کنید",key="calc_input",help="شما میتوانید از نام مجموعه ها برای مختصر نویسی استفاده کنید اگر نام دیگری استفاده کنید با ارور مواجه خواید شد و برای اشتراک از & و برای اجتماع از | استفاده کنید")
                        col2,col1=st.columns(2)
                        submit_btn=col1.form_submit_button("محاسبه جواب",help="با زدن این دکمه جواب عبارت برای شما محاسبه می شود")
                        col2.write(f"<div style='display: flex;justify-content: center;'>{st.session_state["calc_result"]}</div>",unsafe_allow_html=True)
                    if submit_btn:
                        self.calc_sets()
                
    def calc_sets(self):
        fixed_set = SetsAlgorithm.fix_set_variables(str(self.calc_input))
        result = self.sets.U_I_Ms_advance(fixed_set)
        st.session_state["calc_result"] = result
        st.rerun()
if __name__ == "__main__":
    App()