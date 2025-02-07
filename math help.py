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
    def subsets_one_set(given_set):
        num_sub = 2 ** len(given_set)
        subsets_dict = {f" زیرمجموعه{i}عضوی": [] for i in range(len(given_set) + 1)}
        for i in range(len(given_set) + 1):
            for subset in itertools.combinations(given_set, i):
                subsets_dict[f" زیرمجموعه{i}عضوی"].append(subset)
        return subsets_dict

    def subsets_all_sets(self):
        self.subsets_all = {}
        num_of_set = 1
        for i in self.set_of_sets:
            self.subsets_all[f"set{num_of_set}"] = self.subsets_one_set(i)
            num_of_set += 1

    @staticmethod
    def partitions(given_set):
        if len(given_set)<=5:
            return list(more_itertools.set_partitions(given_set))
        else:
            partition_list=[]
            partition_loop=0
            for partition in more_itertools.set_partitions(given_set):
                if partition_loop<=100:
                    partition_list.append(partition) 
                    partition_loop+=1
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
            "set_lengths": {f"Set {i+1} length": len(s) for i, s in enumerate(self.sets)},  # طول هر مجموعه
            "subsets_info": {
                f"Set {i+1}": {
                    f"Set {j+1}": set(self.sets[i]).issubset(set(self.sets[j]))  # بررسی زیرمجموعه بودن
                    for j in range(self.num_sets) if i != j  # جلوگیری از مقایسه خود مجموعه با خودش
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
        text = text.replace('∩', '&').replace('∪', '|').upper()
        
        # Create a dictionary of set variables
        variables = {}
        for name, set_val in self.set_of_sets.items():
            variables[name] = set_val
        
        try:
            # Ensure the expression contains only set operations
            if any(char.isdigit() for char in text):
                return "Error: Numeric operations are not supported."
            
            # Evaluate the expression using the variables dictionary
            result = eval(text, {"__builtins__": {}}, variables)
            return result
        except Exception as e:
            return f"Error evaluating expression: {e}"


    def draw_venn(self, output_path=None):
        if self.num_sets == 3:
            set_one, set_two, set_three = self.sets
            subsets = {
                '100': len(set_one - set_two - set_three),
                '010': len(set_two - set_one - set_three),
                '110': len(set_one & set_two - set_three),
                '001': len(set_three - set_one - set_two),
                '101': len(set_one & set_three - set_two),
                '011': len(set_two & set_three - set_one),
                '111': len(set_one & set_two & set_three)
            }
            venn = matplotlib_venn.venn3(subsets=subsets, set_labels=('Set 1', 'Set 2', 'Set 3'))
            plt.title("Venn Diagram for Three Sets")
            if venn.get_label_by_id('100'):
                venn.get_label_by_id('100').set_text(set_one - set_two - set_three)
            if venn.get_label_by_id('010'):
                venn.get_label_by_id('010').set_text(set_two - set_one - set_three)
            if venn.get_label_by_id('110'):
                venn.get_label_by_id('110').set_text(set_one & set_two - set_three)
            if venn.get_label_by_id('001'):
                venn.get_label_by_id('001').set_text(set_three - set_one - set_two)
            if venn.get_label_by_id('101'):
                venn.get_label_by_id('101').set_text(set_one & set_three - set_two)
            if venn.get_label_by_id('011'):
                venn.get_label_by_id('011').set_text(set_two & set_three - set_one)
            if venn.get_label_by_id('111'):
                venn.get_label_by_id('111').set_text(set_one & set_two & set_three)
        elif self.num_sets == 2:
            set_one, set_two = self.sets
            subsets = {
                '10': len(set_one - set_two),
                '01': len(set_two - set_one),
                '11': len(set_one & set_two)
            }
            venn = matplotlib_venn.venn2(subsets=subsets, set_labels=('Set 1', 'Set 2'))
            plt.title("Venn Diagram for Two Sets")
            venn.get_label_by_id('10').set_text(set_one - set_two)
            venn.get_label_by_id('01').set_text(set_two - set_one)
            venn.get_label_by_id('11').set_text(set_one & set_two)
        else:
            print("Drawing Venn diagrams for less than 2 sets is not supported.")
            return

        if output_path:
            plt.savefig(output_path)
        plt.show()

    def draw_venn_4_more(self, output_path=None):
        venn_data = {self.set_names[i]: self.sets[i] for i in range(self.num_sets)}
        venn(venn_data)
        plt.title(f"Venn Diagram for {self.num_sets} Sets")

        if output_path:
            plt.savefig(output_path)
        return self.get_region_info()

    def get_region_info(self):
        result = {}
        sets_names = self.set_names
        sets_dict = self.set_of_sets
        n = self.num_sets

        for r in range(1, n + 1):
            for include in itertools.combinations(range(n), r):
                included_sets = [sets_names[i] for i in include]
                excluded_sets = [sets_names[i] for i in range(n) if i not in include]

                region = set.intersection(*[sets_dict[name] for name in included_sets])
                for name in excluded_sets:
                    region = region - sets_dict[name]

                if region:
                    notation = '∩'.join(included_sets)
                    if excluded_sets:
                        notation += '-' + '-'.join(excluded_sets)
                    result[notation] = region

        return result

class App():
    def __init__(self,root):
        self.root=root
        style = sttk.ttk.Style()
        sttk.use_dark_theme()
        style.configure("TButton", font=("B Morvarid", 20), padding=10, foreground="white")
        style.configure("Switch.TCheckbutton", font=("B Morvarid", 15),padding=0)
        style.configure("TNotebook.Tab", font=("B Morvarid", 15), padding=5, borderwidth=0, relief="flat", highlightthickness=0,anchor="center")
        style.configure("Treeview.Heading", font=("B Morvarid", 14, "bold"))
        style.configure("Treeview", font=("B Morvarid", 12))
        sttk.use_light_theme()
        style.configure("TButton", font=("B Morvarid", 20), padding=10, foreground="black")
        style.configure("Switch.TCheckbutton", font=("B Morvarid", 15),padding=0)
        style.configure("TNotebook.Tab", font=("B Morvarid", 15), padding=5, borderwidth=0, relief="flat", highlightthickness=0,anchor="center")
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
        self.clear_screen(clear_main_frame=True, all=True,clear_footer=True)
        self.root.resizable(False,False)
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(side='top',fill="both",expand=True)
        self.them_swiwch=ttk.Checkbutton(self.main_frame,text="حالت تاریک",command=self.change_theme,style="Switch.TCheckbutton",variable=self.switch_var,)
        self.them_swiwch.pack(side='left',fill="none",expand=True,padx=10,pady=10)
        frame_section_button = tk.Frame(self.root)
        self.frame_footer = tk.Frame(self.root)
        frame_section_button.pack(side="top", fill="both",expand=True,padx=10,pady=10) 
        self.frame_footer.pack(side='bottom',fill='both',expand=True,padx=10,pady=10)
        enter_sets_button = ttk.Button(frame_section_button,text="مجموعه ها",command=self.enter_sets) 
        enter_sets_button.pack(side="right",fill="x",expand=True,padx=10,pady=10)
        enter_L_equation_button = ttk.Button(frame_section_button,text="مختصات",command=self.enter_L_equation)
        enter_L_equation_button.pack(side="left",fill="x",expand=True,padx=10,pady=10)
        self.exit_button = ttk.Button(self.frame_footer,text="خروج",command=self.root.destroy)
        self.exit_button.pack(side="right",fill="x",expand=True,padx=10,pady=10)
        self.about_button = ttk.Button(self.frame_footer,text=" درباره ما",command=self.about)
        self.about_button.pack(side="right",fill="x",expand=True,padx=10,pady=10)
        self.information_button = ttk.Button(self.frame_footer,text="نحو کار در این بخش",command=lambda: self.information("home_page"))
        self.information_button.pack(side="right",fill="x",expand=True,padx=10,pady=10)
        
    def clear_screen(self, clear_main_frame=False, all=False ,clear_footer=False):
        try:
            # Safely destroy all widgets except main_frame and frame_footer
            for widget in self.root.winfo_children():
                if widget not in [getattr(self, 'main_frame', None), 
                                getattr(self, 'frame_footer', None),
                                getattr(self, 'exit_button', None),
                                getattr(self, 'about_button', None),
                                getattr(self, 'information_button', None),
                                ]:
                    widget.destroy()
            if  clear_footer:
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
            # Recreate main_frame if it was destroyed
            self.main_frame = ttk.Frame(self.root)
            self.main_frame.pack(side='top', fill="both", expand=True)

    def enter_sets(self):
        self.clear_screen(clear_main_frame=True)
        self.advance_var = tk.BooleanVar(value=False)
        self.advance_swiwch=ttk.Checkbutton(self.main_frame,text="حالت پیشرفته",style="Switch.TCheckbutton",variable=self.advance_var,)
        self.advance_swiwch.pack(side='right',fill="none",expand=True,pady=10,ipadx=0)
        frame_section_button = tk.Frame(self.root)
        frame_section_button.pack(side="top", fill="both",expand=True,padx=10,pady=10) 
        more_set= ttk.Button(frame_section_button,text="چند مجموعه ",command=self.sets_section) 
        more_set.pack(side="right",fill="x",expand=True,padx=10,pady=10)
        one_set= ttk.Button(frame_section_button,text="تک مجموعه ",command=self.set_section)
        one_set.pack(side="left",fill="x",expand=True,padx=10,pady=10)
        self.information_button.config(command=lambda :self.information("set_choice"))
        self.exit_button.config(text="صفحه قبل",command=self.main_page)

        

    def enter_L_equation():
        pass
    def about():
        pass
    def information(self,page):
        pass
    def sets_section(self):
        pass
    def set_section(self):
        self.clear_screen()
        self.information_button.config(command=lambda :self.information("set_page"))
        self.exit_button.config(text="صفحه قبل",command=self.enter_sets)
        self.advance_swiwch.config(state="disabled")
        frame_section_set = tk.Frame(self.root)
        frame_section_set.pack(side="top", fill="both",expand=True,padx=10,pady=10) 
        freame_entery_set=ttk.Frame(frame_section_set)
        freame_entery_set.pack(side="top", fill="both",expand=True,pady=10)
        freame_entery_name=ttk.Frame(frame_section_set)
        freame_entery_name.pack(side="bottom", fill="both",expand=True,padx=10,pady=10)
        freame_entery_set_entry=ttk.Frame(freame_entery_set)
        freame_entery_set_entry.pack(side="left", fill="both",expand=True,padx=10,pady=10)
        entry_label=ttk.Label(freame_entery_set_entry,text="مجموعه را وارد کنید",font=("B Morvarid", 15))
        entry_label.pack(side="right", fill="none", expand=False, pady=10 ,padx=10)
        name_label=ttk.Label(freame_entery_name,text="نام مجموعه را وارد کنید",font=("B Morvarid", 15))
        name_label.pack(side="right", fill="none", expand=False, pady=10)
        self.set=tk.StringVar()
        self.set_name=tk.StringVar()
        self.sets_entry = ttk.Entry(freame_entery_set_entry, font=("B Morvarid", 20),textvariable=self.set)
        self.sets_entry.pack(side="top", fill="x", expand=True, padx=10, pady=10,ipadx=5,ipady=5)
        self.sets_entry_name=ttk.Entry(freame_entery_name, font=("B Morvarid", 20),textvariable=self.set_name,validate="key",validatecommand=(self.root.register(lambda text:len(text)<=1),"%P"))
        self.sets_entry_name.pack(side="top", fill="x", expand=True, padx=10, pady=10,ipadx=5,ipady=5)
        next_button = ttk.Button(self.root, text="بعدی", command=self.check_entry)
        next_button.pack(side="bottom", fill="x", expand=True, padx=20, pady=10)
        scroolbar_set_entery = ttk.Scrollbar(freame_entery_set_entry, orient="horizontal", command=self.sets_entry.xview)
        self.sets_entry.config(xscrollcommand=scroolbar_set_entery.set)
        scroolbar_set_entery.pack(side="bottom", fill="x", expand=True,padx=10)
    def change_theme(self):
        if sttk.get_theme() == "dark":
            sttk.use_light_theme()
        elif sttk.get_theme() == "light":
            sttk.use_dark_theme()
    def check_entry(self):
        pattern = r"^\{\s*(\d+\s*(,\s*\d+\s*)*)?\}$"
        entry_value = self.set.get().strip() 
    
        if not entry_value.startswith("{") or not entry_value.endswith("}"):
            messagebox.showerror("ERROR", "وارد شده باید با { شروع شود و با } به اتمام برسد")
            return
        
        content = entry_value[1:-1].strip()
        
        if content and not re.fullmatch(pattern, entry_value):
            messagebox.showerror(" ERROR ", " اعضای مجموعه باید فقط از اعداد تشکیل شده و با کاما جدا شوند!")
            return 
        
        if not self.set_name.get() or self.set_name.get().isdigit():
            messagebox.showerror("ERROR", "نمیتوانید نام مجموعه را خالی بگذارید یا عدد وارد کنید")
            return
        
        if self.set_name.get().islower():
            messagebox.showwarning("warning", "که وارد کردید به حروف بزرگ تبدیل شد")
            self.set_name.set(self.set_name.get().strip().upper())
        self.set_info_page()
    def set_info_page(self):
        set = eval(self.set.get())
        set_name = self.set_name.get()
        subsets= SetsAlgorithm.subsets_one_set(set)
        partitions = SetsAlgorithm.partitions(set)        
        self.clear_screen()
        information_frame = tk.Frame(self.root)
        information_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        information_set=tk.Frame(information_frame)
        information_set.pack(side="top",fill="both",expand=True,padx=10,pady=10)
        name_label=ttk.Label(information_set,text=f"{set_name} : نام مجموعه ",font=("B Morvarid",15))
        name_label.pack(side="right",fill="none",expand=True,padx=10)
        set_label=ttk.Label(information_set,text=f"{set} : اعضای مجموعه ",font=("B Morvarid",15))
        set_label.pack(side="left",fill="none",expand=True,padx=10)
        set_len=ttk.Label(information_set,text=f"{len(set)} :  طول مجموعه ",font=("B Morvarid",15))
        set_len.pack(side="bottom",fill="none",padx=10,pady=10)
        tab_info=ttk.Notebook(information_frame)
        tab_info.pack(side="bottom",fill="both",expand=True,padx=10,pady=10)
        partition_frame=tk.Frame(tab_info)
        subset_frame=tk.Frame(tab_info)
        tab_info.add(partition_frame,text="افراز ها")
        tab_info.add(subset_frame,text="زیر مجموعه ها")
        tree_viwe_par=ttk.Treeview(partition_frame,columns=("par"))
        tree_viwe_par.heading("#0", text="شماره افراز")
        tree_viwe_par.heading("par", text=" اعضای افراز")
        tree_viwe_par.column("#0", width=50)
        tree_viwe_par.column("par", width=100)
        for i, partition in enumerate(partitions):
            partition_str = " , ".join([f"{{{', '.join(map(str, subset))}}}" for subset in partition])
            partition_str = f"{{{{{partition_str}}}}}"
            
            tree_viwe_par.insert("", "end", text=str(i+1), values=( partition_str))
        scrollbar = ttk.Scrollbar(partition_frame, orient="vertical", command=tree_viwe_par.yview)
        scrollbar.pack(side="right", fill="y",pady=10)
        tree_viwe_par.config(yscrollcommand=scrollbar.set)
        
        tree_viwe_par.pack(side="left", fill="both", expand=True)
        set_len=ttk.Label(subset_frame,text=f"تعداد زیر مجموعه ها : {2**len(set)}",font=("B Morvarid",15))
        set_len.pack(side="top",fill="none",padx=10,pady=10)
        tree_viwe_sub = ttk.Treeview(subset_frame, columns=("members"))
        tree_viwe_sub.heading("#0", text="زیر مجموعه")
        tree_viwe_sub.heading("members", text="اعضاء")
        tree_viwe_sub.column("#0", width=150)
        tree_viwe_sub.column("members", width=250)
        # افزودن داده‌ها به Treeview زیر مجموعه‌ها
        for subset_name, subset_items in subsets.items():
            parent = tree_viwe_sub.insert("", "end", text=subset_name, open=False)
            number_loop = 1
            for item in subset_items:
                # تبدیل هر عضو به فرمت مجموعه، یعنی {1, 2, 34} به جای (1, 2, 34)
                item_str = "{" + ", ".join(map(str, item)) + "}"
                tree_viwe_sub.insert(parent, "end", text=number_loop, values=(item_str,))
                number_loop += 1


        # افزودن اسکرول بار عمودی به Treeview زیر مجموعه‌ها
        scrollbar_sub = ttk.Scrollbar(subset_frame, orient="vertical", command=tree_viwe_sub.yview)
        scrollbar_sub.pack(side="right", fill="y", pady=10)
        tree_viwe_sub.config(yscrollcommand=scrollbar_sub.set)
        tree_viwe_sub.pack(side="left",expand=True, fill="both", padx=10, pady=10)




print(SetsAlgorithm.subsets_one_set({1,2,34,5}))
App(tk.Tk())
tk.mainloop()

