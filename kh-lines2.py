import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

class LineIntersectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("رسم خطوط و محاسبه نقطه تقاطع")
        
        self.transformations = standard_transformations + (implicit_multiplication_application,)
        
        self.main_page()

    def parse_equation(self, equation):
        x, y = sp.symbols('x y')
        try:
            expr = sp.sympify(equation)
            if y not in expr.free_symbols:
                expr = sp.Eq(y, expr)
            elif '=' in equation:
                lhs, rhs = equation.split('=')
                expr = sp.Eq(sp.sympify(lhs), sp.sympify(rhs))
            else:
                raise ValueError("Invalid equation format")
            solved_expr = sp.solve(expr, y)
            m, b = sp.simplify(solved_expr[0].as_coefficients_dict()[x]), sp.simplify(solved_expr[0].as_coefficients_dict()[1])
            return float(m), float(b)
        except Exception as e:
            raise ValueError("Invalid equation format")

    def get_line_from_points(self, point1, point2):
        try:
            x1, y1 = map(float, point1.split(','))
            x2, y2 = map(float, point2.split(','))
        except Exception:
            raise ValueError("فرمت نقطه‌ای نامعتبر است. فرمت صحیح: x,y")
        if x1 == x2:
            raise ValueError("برای رسم خط، مقادیر x نقاط باید متفاوت باشند (خط عمودی پشتیبانی نمی‌شود).")
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1
        return m, b

    def calculate_and_plot(self):
        try:
            # پردازش خط اول (با توجه به حالت انتخاب شده: معادله یا نقاط)
            if self.line1_mode.get() == "equation":
                eq1 = self.entry_line1.get()
                m1, b1 = self.parse_equation(eq1)
            else:
                pt1 = self.entry_line1_point1.get()
                pt2 = self.entry_line1_point2.get()
                m1, b1 = self.get_line_from_points(pt1, pt2)
                
            # پردازش خط دوم
            if self.line2_mode.get() == "equation":
                eq2 = self.entry_line2.get()
                m2, b2 = self.parse_equation(eq2)
            else:
                pt3 = self.entry_line2_point1.get()
                pt4 = self.entry_line2_point2.get()
                m2, b2 = self.get_line_from_points(pt3, pt4)
            
            # رسم خطوط در بازه x از -20 تا 20
            x_vals = np.linspace(-20, 20, 400)
            y_vals1 = m1 * x_vals + b1
            y_vals2 = m2 * x_vals + b2

            plt.figure(figsize=(6,4))
            plt.plot(x_vals, y_vals1, label=f'خط اول: y = {m1:.2f}x + {b1:.2f}')
            plt.plot(x_vals, y_vals2, label=f'خط دوم: y = {m2:.2f}x + {b2:.2f}')
            plt.axhline(0, color='black', linewidth=0.5)
            plt.axvline(0, color='black', linewidth=0.5)
            plt.grid(True, linestyle='--', linewidth=0.5)
            plt.xlabel("x")
            plt.ylabel("y")
            plt.title("رسم خطوط و محاسبه نقطه تقاطع")
            plt.legend()

            # محاسبه نقطه تقاطع (در صورتی که خطوط موازی نباشند)
            if m1 != m2:
                xi = (b2 - b1) / (m1 - m2)
                yi = m1 * xi + b1
                plt.scatter([xi], [yi], color='red', zorder=5)
                messagebox.showinfo("نقطه تقاطع", f"نقطه تقاطع: ({xi:.2f}, {yi:.2f})")
            else:
                messagebox.showinfo("نقطه تقاطع", "خطوط موازی هستند و نقطه تقاطع ندارند.")

            plt.show()
        except Exception as e:
            messagebox.showerror("خطا", str(e))

    def update_line1_inputs(self):
        if self.line1_mode.get() == "equation":
            self.label_line1.grid()
            self.entry_line1.grid()
            self.label_line1_pt1.grid_remove()
            self.entry_line1_point1.grid_remove()
            self.label_line1_pt2.grid_remove()
            self.entry_line1_point2.grid_remove()
        else:
            self.label_line1.grid_remove()
            self.entry_line1.grid_remove()
            self.label_line1_pt1.grid(row=1, column=0, sticky="w", pady=5)
            self.entry_line1_point1.grid(row=1, column=1, sticky="w", pady=5)
            self.label_line1_pt2.grid(row=2, column=0, sticky="w", pady=5)
            self.entry_line1_point2.grid(row=2, column=1, sticky="w", pady=5)

    def update_line2_inputs(self):
        if self.line2_mode.get() == "equation":
            self.label_line2.grid()
            self.entry_line2.grid()
            self.label_line2_pt1.grid_remove()
            self.entry_line2_point1.grid_remove()
            self.label_line2_pt2.grid_remove()
            self.entry_line2_point2.grid_remove()
        else:
            self.label_line2.grid_remove()
            self.entry_line2.grid_remove()
            self.label_line2_pt1.grid(row=1, column=0, sticky="w", pady=5)
            self.entry_line2_point1.grid(row=1, column=1, sticky="w", pady=5)
            self.label_line2_pt2.grid(row=2, column=0, sticky="w", pady=5)
            self.entry_line2_point2.grid(row=2, column=1, sticky="w", pady=5)

    def main_page(self):
        # ایجاد پنجره اصلی
        self.root.title("رسم خطوط و محاسبه نقطه تقاطع")

        # -------------------------- بخش ورودی خط اول --------------------------
        frame_line1 = ttk.LabelFrame(self.root, text="خط اول", padding=10)
        frame_line1.pack(padx=10, pady=10, fill="both", expand=True)

        # انتخاب حالت ورودی: معادله یا نقطه‌ای
        self.line1_mode = tk.StringVar(value="equation")
        rbtn_line1_eq = ttk.Radiobutton(frame_line1, text="معادله", variable=self.line1_mode, value="equation", command=self.update_line1_inputs)
        rbtn_line1_pts = ttk.Radiobutton(frame_line1, text="نقطه‌ای", variable=self.line1_mode, value="points", command=self.update_line1_inputs)
        rbtn_line1_eq.grid(row=0, column=0, sticky="w")
        rbtn_line1_pts.grid(row=0, column=1, sticky="w")

        # بخش ورود معادله برای خط اول
        self.label_line1 = ttk.Label(frame_line1, text="معادله خط اول:")
        self.label_line1.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        self.entry_line1 = ttk.Entry(frame_line1, width=40)
        self.entry_line1.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        # بخش ورود نقاط برای خط اول (دو نقطه)
        self.label_line1_pt1 = ttk.Label(frame_line1, text="نقطه ۱ (x,y):")
        self.entry_line1_point1 = ttk.Entry(frame_line1, width=20)
        self.label_line1_pt2 = ttk.Label(frame_line1, text="نقطه ۲ (x,y):")
        self.entry_line1_point2 = ttk.Entry(frame_line1, width=20)

        self.update_line1_inputs()  # به‌روزرسانی اولیه نمایش

        # -------------------------- بخش ورودی خط دوم --------------------------
        frame_line2 = ttk.LabelFrame(self.root, text="خط دوم", padding=10)
        frame_line2.pack(padx=10, pady=10, fill="both", expand=True)

        # انتخاب حالت ورودی برای خط دوم
        self.line2_mode = tk.StringVar(value="equation")
        rbtn_line2_eq = ttk.Radiobutton(frame_line2, text="معادله", variable=self.line2_mode, value="equation", command=self.update_line2_inputs)
        rbtn_line2_pts = ttk.Radiobutton(frame_line2, text="نقطه‌ای", variable=self.line2_mode, value="points", command=self.update_line2_inputs)
        rbtn_line2_eq.grid(row=0, column=0, sticky="w")
        rbtn_line2_pts.grid(row=0, column=1, sticky="w")

        # بخش ورود معادله برای خط دوم
        self.label_line2 = ttk.Label(frame_line2, text="معادله خط دوم:")
        self.label_line2.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        self.entry_line2 = ttk.Entry(frame_line2, width=40)
        self.entry_line2.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        # بخش ورود نقاط برای خط دوم (دو نقطه)
        self.label_line2_pt1 = ttk.Label(frame_line2, text="نقطه ۱ (x,y):")
        self.entry_line2_point1 = ttk.Entry(frame_line2, width=20)
        self.label_line2_pt2 = ttk.Label(frame_line2, text="نقطه ۲ (x,y):")
        self.entry_line2_point2 = ttk.Entry(frame_line2, width=20)

        self.update_line2_inputs()  # به‌روزرسانی اولیه

        # دکمه محاسبه و رسم
        btn_calculate = ttk.Button(self.root, text="محاسبه و رسم", command=self.calculate_and_plot)
        btn_calculate.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = LineIntersectionApp(root)
    root.mainloop()