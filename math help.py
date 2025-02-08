import itertools
import more_itertools
import matplotlib.pyplot as plt
import matplotlib_venn
import tkinter as tk
import tkinter.ttk as ttk
import sv_ttk as sttk
from venn import venn
import darkdetect
from tkinter import messagebox
import re

# نکته: ما تغییر __repr__ را اعمال نمی‌کنیم؛ فقط از توابع کمکی set_to_str برای نمایش زیبا استفاده می‌کنیم.

class SetsAlgorithm:
    def __init__(self, set_of_sets):
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
    def parse_set_string(s, advance_u=False):
        s = s.strip()
        if not (s.startswith("{") and s.endswith("}")):
            return s
        # حذف آکولادهای بیرونی
        content = s[1:-1].strip()
        if content == "":
            return "frozenset()"
        elements = []
        current = ""
        depth = 0
        for char in content:
            if char == '{':
                depth += 1
                current += char
            elif char == '}':
                depth -= 1
                current += char
            elif char == ',' and depth == 0:
                elements.append(current.strip())
                current = ""
            else:
                current += char
        if current:
            elements.append(current.strip())
        parsed_elements = []
        for elem in elements:
            # اگر عنصری دوباره به صورت مجموعه نوشته شده باشد، به‌صورت بازگشتی پردازش می‌شود
            if elem.startswith("{") and elem.endswith("}"):
                parsed_elements.append(SetsAlgorithm.parse_set_string(elem))
            else:
                parsed_elements.append(elem)
        inner_expr = ", ".join(parsed_elements)
        return f"frozenset({{{inner_expr}}})"

    @staticmethod
    def fix_set_variables(expression):
        """
        اگر عبارت ورودی مجموعه نباشد، پیام خطا نمایش می‌دهد.
        در داخل هر جفت آکولاد، اگر عنصری عدد نباشد و یا در کوتیشن نباشد،
        به‌طور خودکار آن را به حروف بزرگ در داخل کوتیشن قرار می‌دهد.
        """
        if not (expression.startswith("{") and expression.endswith("}")):
            messagebox.showerror("ERROR", "ورودی باید با { شروع و با } تمام شود")
            return expression

        def replacer(match):
            inner_content = match.group(1)
            tokens = inner_content.split(",")
            fixed_tokens = []
            for token in tokens:
                token = token.strip()
                if token == "":
                    continue
                # اگر token عدد باشد یا از قبل در کوتیشن قرار داشته باشد، همان نگه داشته شود.
                if token.isdigit() or ((token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'"))):
                    fixed_tokens.append(token)
                else:
                    # در اینجا فرض می‌کنیم token شامل حروف یا اعداد و حروف است؛ آن را به صورت خودکار به حروف بزرگ در داخل کوتیشن قرار می‌دهیم.
                    if token.isalpha() or token.isalnum():
                        fixed_tokens.append(f'"{token.upper()}"')
                    else:
                        messagebox.showerror("ERROR", f"مقدار '{token}' باید به صورت صحیح تعریف شود.")
                        fixed_tokens.append(token)
            return "{" + ", ".join(fixed_tokens) + "}"

        fixed_expression = re.sub(r"\{([^{}]*)\}", replacer, expression)
        return fixed_expression

    @staticmethod
    def to_frozenset(obj):
        if isinstance(obj, (set, frozenset)):
            return frozenset(SetsAlgorithm.to_frozenset(x) for x in obj)
        return obj

    @staticmethod
    def subsets_one_set(given_set):
        num_loop = 0
        # اگر ورودی به صورت رشته نباشد، آن را به رشته تبدیل می‌کنیم
        if not isinstance(given_set, str):
            given_set = repr(given_set)
        given_set = eval(given_set)
        if len(given_set) >= 11:
            subsets_dict = {f" زیرمجموعه{i}عضوی": [] for i in range(11)}
        else:
            subsets_dict = {f" زیرمجموعه{i}عضوی": [] for i in range(len(given_set)+1)}
        for i in range(len(given_set) + 1):
            if num_loop > 10:
                break
            for subset in itertools.combinations(given_set, i):
                subsets_dict[f" زیرمجموعه{i}عضوی"].append(subset)
            num_loop += 1
        return subsets_dict

    def subsets_all_sets(self):
        self.subsets_all = {}
        num_of_set = 1
        for i in self.set_of_sets:
            self.subsets_all[f"set{num_of_set}"] = self.subsets_one_set(i)
            num_of_set += 1

    @staticmethod
    def partitions(given_set):
        if len(given_set) <= 5:
            return list(more_itertools.set_partitions(given_set))
        else:
            partition_list = []
            partition_loop = 0
            for partition in more_itertools.set_partitions(given_set):
                if partition_loop <= 100:
                    partition_list.append(partition)
                    partition_loop += 1
                else:
                    break
            return partition_list

    def U(self, bitmask):
        return set().union(*(self.sets[i] for i in range(self.num_sets) if bitmask & (1 << i)))

    def I(self, bitmask):
        selected_sets = [self.sets[i] for i in range(self.num_sets) if bitmask & (1 << i)]
        return set.intersection(*selected_sets)

    def Ms(self, bitmask, target_bit):
        main_set = self.sets[target_bit]
        other_sets = self.U(bitmask & ~(1 << target_bit))
        return main_set - other_sets

    def check_other_information(self):
        info = {
            "set_lengths": {f"Set {i+1} length": len(s) for i, s in enumerate(self.sets)},
            "subsets_info": {
                f"Set {i+1}": {
                    f"Set {j+1}": set(self.sets[i]).issubset(set(self.sets[j]))
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
        """
        این متد عبارت ورودی کاربر (با عملگرهایی مانند اتحاد، اشتراک و تفاوت) را دریافت می‌کند.
        ابتدا ورودی با parse_set_string به عبارتی صحیح تبدیل می‌شود؛ سپس eval شده و در نهایت
        نتیجه به صورت رشته‌ای با آکولاد (بدون ذکر "frozenset") به کاربر نمایش داده می‌شود.
        """
        text = text.replace('∩', '&').replace('∪', '|')
        allowed_chars = set(" {}(),|&-0123456789'\"")
        if not all(ch in allowed_chars or ch.isalpha() for ch in text):
            messagebox.showerror("ارور", "(جهت آشنایی با کاراکترهای پشتیبانی شده وارد بخش نحوه کار در این بخش شوید)خطا: کاراکترهای نامعتبر شناسایی شد.")
            return "در انتظار دریافت عبارت..."
        
        transformed_text = SetsAlgorithm.parse_set_string(text, advance_u=True)
        variables = {name: frozenset(set_val) for name, set_val in self.set_of_sets.items()}
        
        try:
            result = eval(transformed_text, {"__builtins__": {}, "frozenset": frozenset}, variables)
            return self.set_to_str(result)
        except Exception as e:
            messagebox.showerror("ارور", f"خطا در ارزیابی عبارت: {e}")
            return "در انتظار دریافت عبارت..."

    @staticmethod
    def convert_set_item(item):
        if isinstance(item, frozenset):
            return "{" + ", ".join(SetsAlgorithm.convert_set_item(sub_item) for sub_item in item) + "}"
        return str(item)

    @staticmethod
    def set_to_str(result):
        if isinstance(result, frozenset):
            return "{" + ", ".join(SetsAlgorithm.convert_set_item(item) for item in result) + "}"
        elif isinstance(result, set):
            return "{" + ", ".join(str(item) for item in result) + "}"
        return str(result)

class App():
    def __init__(self, root):
        self.root = root
        style = sttk.ttk.Style()
        sttk.use_dark_theme()
        style.configure("TButton", font=("B Morvarid", 20), padding=10, foreground="white")
        style.configure("Switch.TCheckbutton", font=("B Morvarid", 15), padding=0)
        style.configure("TNotebook.Tab", font=("B Morvarid", 15), padding=5, borderwidth=0, relief="flat", highlightthickness=0, anchor="center")
        style.configure("Treeview.Heading", font=("B Morvarid", 14, "bold"))
        style.configure("Treeview", font=("B Morvarid", 12))
        sttk.use_light_theme()
        style.configure("TButton", font=("B Morvarid", 20), padding=10, foreground="black")
        style.configure("Switch.TCheckbutton", font=("B Morvarid", 15), padding=0)
        style.configure("TNotebook.Tab", font=("B Morvarid", 15), padding=5, borderwidth=0, relief="flat", highlightthickness=0, anchor="center")
        style.configure("Treeview.Heading", font=("B Morvarid", 14, "bold"))
        style.configure("Treeview", font=("B Morvarid", 12))
        sttk.set_theme(darkdetect.theme())
        self.switch_var = tk.BooleanVar()
        if sttk.get_theme() == "dark":
            self.switch_var.set(True)
        elif sttk.get_theme() == "light":
            self.switch_var.set(False)
        self.main_page()

    def main_page(self):
        if not hasattr(self, 'main_frame'):
            self.main_frame = ttk.Frame(self.root)
        if not hasattr(self, 'frame_footer'):
            self.frame_footer = ttk.Frame(self.root)
        if sttk.get_theme() == "dark":
            self.switch_var.set(True)
        elif sttk.get_theme() == "light":
            self.switch_var.set(False)
        self.clear_screen(clear_main_frame=True, all=True, clear_footer=True)
        self.root.resizable(False, False)
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(side='top', fill="both", expand=True)
        self.them_swiwch = ttk.Checkbutton(self.main_frame, text="حالت تاریک", command=self.change_theme, style="Switch.TCheckbutton", variable=self.switch_var)
        self.them_swiwch.pack(side='left', fill="none", expand=True, padx=10, pady=10)
        frame_section_button = tk.Frame(self.root)
        self.frame_footer = tk.Frame(self.root)
        frame_section_button.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.frame_footer.pack(side='bottom', fill='both', expand=True, padx=10, pady=10)
        enter_sets_button = ttk.Button(frame_section_button, text="مجموعه ها", command=self.enter_sets)
        enter_sets_button.pack(side="right", fill="x", expand=True, padx=10, pady=10)
        enter_L_equation_button = ttk.Button(frame_section_button, text="مختصات", command=self.enter_L_equation)
        enter_L_equation_button.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.exit_button = ttk.Button(self.frame_footer, text="خروج", command=self.root.destroy)
        self.exit_button.pack(side="right", fill="x", expand=True, padx=10, pady=10)
        self.about_button = ttk.Button(self.frame_footer, text=" درباره ما", command=self.about)
        self.about_button.pack(side="right", fill="x", expand=True, padx=10, pady=10)
        self.information_button = ttk.Button(self.frame_footer, text="نحو کار در این بخش", command=lambda: self.information("home_page"))
        self.information_button.pack(side="right", fill="x", expand=True, padx=10, pady=10)

    def clear_screen(self, clear_main_frame=False, all=False, clear_footer=False):
        try:
            for widget in self.root.winfo_children():
                if widget not in [getattr(self, 'main_frame', None),
                                  getattr(self, 'frame_footer', None),
                                  getattr(self, 'exit_button', None),
                                  getattr(self, 'about_button', None),
                                  getattr(self, 'information_button', None)]:
                    widget.destroy()
            if clear_footer:
                self.frame_footer.destroy()
            if clear_main_frame and hasattr(self, 'main_frame'):
                if all:
                    self.main_frame.destroy()
                    self.main_frame = ttk.Frame(self.root)
                    self.main_frame.pack(side='top', fill="both", expand=True)
                else:
                    for item in self.main_frame.winfo_children():
                        if item != getattr(self, 'them_swiwch', None):
                            item.destroy()
        except tk.TclError:
            self.main_frame = ttk.Frame(self.root)
            self.main_frame.pack(side='top', fill="both", expand=True)

    def enter_sets(self):
        self.clear_screen(clear_main_frame=True)
        self.advance_var = tk.BooleanVar(value=False)
        self.advance_swiwch = ttk.Checkbutton(self.main_frame, text="حالت پیشرفته", style="Switch.TCheckbutton", variable=self.advance_var)
        self.advance_swiwch.pack(side='right', fill="none", expand=True, pady=10, ipadx=0)
        frame_section_button = tk.Frame(self.root)
        frame_section_button.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        more_set = ttk.Button(frame_section_button, text="چند مجموعه ", command=self.sets_section)
        more_set.pack(side="right", fill="x", expand=True, padx=10, pady=10)
        one_set = ttk.Button(frame_section_button, text="تک مجموعه ", command=self.set_section)
        one_set.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.information_button.config(command=lambda: self.information("set_choice"))
        self.exit_button.config(text="صفحه قبل", command=self.main_page)

    def enter_L_equation(self):
        pass

    def about(self):
        pass

    def information(self, page):
        pass

    def sets_section(self):
        pass

    def set_section(self):
        self.clear_screen()
        self.information_button.config(command=lambda: self.information("set_page"))
        self.exit_button.config(text="صفحه قبل", command=self.enter_sets)
        self.advance_swiwch.config(state="disabled")
        frame_section_set = tk.Frame(self.root)
        frame_section_set.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        freame_entery_set = ttk.Frame(frame_section_set)
        freame_entery_set.pack(side="top", fill="both", expand=True, pady=10)
        freame_entery_name = ttk.Frame(frame_section_set)
        freame_entery_name.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)
        freame_entery_set_entry = ttk.Frame(freame_entery_set)
        freame_entery_set_entry.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        entry_label = ttk.Label(freame_entery_set_entry, text="مجموعه را وارد کنید", font=("B Morvarid", 15))
        entry_label.pack(side="right", fill="none", expand=False, pady=10, padx=10)
        name_label = ttk.Label(freame_entery_name, text="نام مجموعه را وارد کنید", font=("B Morvarid", 15))
        name_label.pack(side="right", fill="none", expand=False, pady=10)
        self.set = tk.StringVar()
        self.set_name = tk.StringVar()
        self.sets_entry = ttk.Entry(freame_entery_set_entry, font=("B Morvarid", 20), textvariable=self.set)
        self.sets_entry.pack(side="top", fill="x", expand=True, padx=10, pady=10, ipadx=5, ipady=5)
        self.sets_entry_name = ttk.Entry(freame_entery_name, font=("B Morvarid", 20), textvariable=self.set_name, 
                                          validate="key", validatecommand=(self.root.register(lambda text: len(text) <= 1), "%P"))
        self.sets_entry_name.pack(side="top", fill="x", expand=True, padx=10, pady=10, ipadx=5, ipady=5)
        next_button = ttk.Button(self.root, text="بعدی", command=self.check_entry)
        next_button.pack(side="bottom", fill="x", expand=True, padx=20, pady=10)
        scroolbar_set_entery = ttk.Scrollbar(freame_entery_set_entry, orient="horizontal", command=self.sets_entry.xview)
        self.sets_entry.config(xscrollcommand=scroolbar_set_entery.set)
        scroolbar_set_entery.pack(side="bottom", fill="x", expand=True, padx=10)

    def change_theme(self):
        if sttk.get_theme() == "dark":
            sttk.use_light_theme()
        elif sttk.get_theme() == "light":
            sttk.use_dark_theme()

    def check_entry(self):
        entry_value = self.set.get().strip()
        # بررسی اینکه ورودی با { شروع و با } تمام شود
        if not entry_value.startswith("{") or not entry_value.endswith("}"):
            messagebox.showerror("ERROR", "ورودی باید با { شروع و با } تمام شود")
            return

        # به‌طور خودکار، bare value‌ها (بدون کوتیشن) را اصلاح می‌کنیم
        fixed_entry_value = SetsAlgorithm.fix_set_variables(entry_value)

        # تلاش برای پردازش رشته ورودی جهت شناسایی فرمت‌های تو در تو
        try:
            transformed = SetsAlgorithm.parse_set_string(fixed_entry_value)
            # ارزیابی برای اعتبارسنجی ورودی
            eval_set = eval(transformed, {"__builtins__": {}, "frozenset": frozenset})
        except Exception as e:
            messagebox.showerror("ERROR", f"فرمت مجموعه وارد شده نادرست است:\n{e}")
            return

        if not self.set_name.get() or self.set_name.get().isdigit():
            messagebox.showerror("ERROR", "نمیتوانید نام مجموعه را خالی بگذارید یا عدد وارد کنید")
            return

        if self.set_name.get().islower():
            messagebox.showwarning("Warning", "حروف به صورت بزرگ تبدیل شدند")
            self.set_name.set(self.set_name.get().strip().upper())

        self.set_info_page()

    def set_info_page(self):
        # ابتدا ورودی را اصلاح می‌کنیم تا bare valueها درون کوتیشن قرار گیرند
        fixed_entry = SetsAlgorithm.fix_set_variables(self.set.get())
        transformed = SetsAlgorithm.parse_set_string(fixed_entry)
        try:
            evaluated = eval(transformed, {"__builtins__": {}, "frozenset": frozenset})
            # به صورت بازگشتی همه setهای موجود را به frozenset تبدیل می‌کنیم
            set_obj = SetsAlgorithm.to_frozenset(evaluated)
        except Exception as e:
            messagebox.showerror("ERROR", f"خطا در ارزیابی مجموعه:\n{e}")
            return

        set_name = self.set_name.get()
        subsets = SetsAlgorithm.subsets_one_set(set_obj)
        partitions = SetsAlgorithm.partitions(set_obj)
        self.clear_screen()
        information_frame = tk.Frame(self.root)
        information_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        information_set = tk.Frame(information_frame)
        information_set.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        tab_info = ttk.Notebook(information_frame)
        tab_info.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)
        if self.advance_var.get():
            sets_calc_frame = tk.Frame(information_set)
            sets_calc_frame.pack(side="bottom", fill="both", expand=True)
            calc_label = ttk.Label(sets_calc_frame, text="برای محاسبه اعمال مجموعه عبارت مورد نظر را وارد کنید ", font=("B Morvarid", 20), justify="center")
            calc_label.pack(side="top", fill="y", expand=True, padx=10)
            self.calc_var = tk.StringVar()
            entry_frame = tk.Frame(sets_calc_frame)
            entry_frame.pack(side="top", expand=True, fill="x")
            calc_entry = ttk.Entry(entry_frame, font=("B Morvarid", 20), textvariable=self.calc_var)
            calc_entry.pack(side="right", expand=True, fill="both", padx=10, pady=10, ipadx=10, ipady=10)
            ruselt_frame = tk.Frame(sets_calc_frame)
            ruselt_frame.pack(side="top", expand=True, fill="both")
            ruselt_label_part_1 = ttk.Label(ruselt_frame, text=": جواب", font=("B Morvarid", 20))
            ruselt_label_part_1.pack(side="right", expand=True, fill="y")
            self.ruselt_label_part_2 = ttk.Label(ruselt_frame, text="...در انتظار دریافت عبارت", font=("B Morvarid", 20))
            self.ruselt_label_part_2.pack(side="left", expand=True, fill="y")
            calc_btn = ttk.Button(entry_frame, text="محاسبه", command=self.calc_metod_one_set)
            calc_btn.pack(side="left", expand=True, fill="both", padx=10, pady=10)
            tab_info.pack(side="right", fill="both", expand=True, padx=10, pady=10)
            information_set.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        else:
            tab_info.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)
            information_set.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        name_label = ttk.Label(information_set, text=f"{set_name} : نام مجموعه ", font=("B Morvarid", 15))
        name_label.pack(side="right", fill="none", expand=True, padx=10)
        # استفاده از تابع set_to_str برای نمایش اعضای مجموعه بدون کلمه‌ی frozenset
        set_label = ttk.Label(information_set, text=f"{SetsAlgorithm.set_to_str(set_obj)} : اعضای مجموعه ", font=("B Morvarid", 15))
        set_label.pack(side="left", fill="none", expand=True, padx=10)
        set_len = ttk.Label(information_set, text=f"{len(set_obj)} :  طول مجموعه ", font=("B Morvarid", 15))
        set_len.pack(side="bottom", fill="none", padx=10, pady=10)
        partition_frame = tk.Frame(tab_info)
        subset_frame = tk.Frame(tab_info)
        tab_info.config(height=275)
        tab_info.add(partition_frame, text="افراز ها")
        tab_info.add(subset_frame, text="زیر مجموعه ها")
        tree_viwe_par = ttk.Treeview(partition_frame, columns=("par"))
        tree_viwe_par.heading("#0", text="شماره افراز")
        tree_viwe_par.heading("par", text=" اعضای افراز")
        tree_viwe_par.column("#0", width=50)
        tree_viwe_par.column("par", width=100)
        for i, partition in enumerate(partitions):
            # استفاده از set_to_str برای هر زیرمجموعه موجود در افراز
            partition_str = " , ".join([SetsAlgorithm.set_to_str(frozenset(subset)) for subset in partition])
            partition_str = f"{{{{{partition_str}}}}}"
            tree_viwe_par.insert("", "end", text=str(i+1), values=(partition_str))
        scrollbar = ttk.Scrollbar(partition_frame, orient="vertical", command=tree_viwe_par.yview)
        scrollbar.pack(side="right", fill="y", pady=10)
        tree_viwe_par.config(yscrollcommand=scrollbar.set)
        tree_viwe_par.pack(side="left", fill="both", expand=True)
        set_len_label = ttk.Label(subset_frame, text=f"تعداد کل زیر مجموعه ها : {2**len(set_obj)}", font=("B Morvarid", 15))
        if len(set_obj) > 10:
            set_len_label.config(text=f"تعداد کل زیر مجموعه ها : {2**len(set_obj)} تعداد محاسبه شده : 1024")
        set_len_label.pack(side="top", fill="none", padx=10, pady=10)
        tree_viwe_sub = ttk.Treeview(subset_frame, columns=("members"))
        tree_viwe_sub.heading("#0", text="زیر مجموعه")
        tree_viwe_sub.heading("members", text="اعضاء")
        tree_viwe_sub.column("#0", width=150)
        tree_viwe_sub.column("members", width=250)
        for subset_name, subset_items in SetsAlgorithm.subsets_one_set(set_obj).items():
            parent = tree_viwe_sub.insert("", "end", text=subset_name, open=False)
            number_loop = 1
            for item in subset_items:
                # استفاده از set_to_str برای نمایش زیرمجموعه‌ها به شکل دلخواه
                item_str = SetsAlgorithm.set_to_str(frozenset(item))
                tree_viwe_sub.insert(parent, "end", text=number_loop, values=(item_str,))
                number_loop += 1
        scrollbar_sub = ttk.Scrollbar(subset_frame, orient="vertical", command=tree_viwe_sub.yview)
        scrollbar_sub.pack(side="right", fill="y", pady=10)
        tree_viwe_sub.config(yscrollcommand=scrollbar_sub.set)
        tree_viwe_sub.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        self.exit_button.config(command=self.set_section)
        self.information_button.config(command=lambda: self.information("set_info_page"))

    def calc_metod_one_set(self):
        fixed_set = SetsAlgorithm.fix_set_variables(self.calc_var.get())
        set_oop = SetsAlgorithm({f"{self.set_name.get()}": eval(self.set.get(), {"__builtins__": {}, "frozenset": frozenset})})
        result = set_oop.U_I_Ms_advance(fixed_set)
        if result == self.set.get():
            result = "A"
        self.ruselt_label_part_2.config(text=result)

App(tk.Tk())
tk.mainloop()
