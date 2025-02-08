import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

def parse_equation(equation):
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

def lines():
    equation = entry.get()
    try:
        m, b = parse_equation(equation)
        x = np.linspace(-20, 20, 400)  # افزایش محدوده x برای طولانی‌تر کردن خط
        y = m * x + b

        plt.figure(figsize=(6, 4))
        plt.plot(x, y, label=f'y = {m}x + {b}')
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.grid(color='gray', linestyle='--', linewidth=0.5)
        plt.title('نمودار معادله خطی')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.legend()
        plt.show()
    except Exception as e:
        messagebox.showerror("خطا", "لطفاً یک معادله خطی معتبر به فرم y=mx+b وارد کنید")

def plot_line_from_points():
    try:
        x1, y1 = map(float, entry_x1.get().split(","))
        x2, y2 = map(float, entry_x2.get().split(","))

        if x1 == x2:
            messagebox.showerror("خطا", "نقاط باید دارای مقادیر x متفاوت باشند.")
            return

        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1

        x = np.linspace(min(x1, x2) - 10, max(x1, x2) + 10, 400)  # افزایش محدوده x برای طولانی‌تر کردن خط
        y = m * x + b

        plt.figure(figsize=(6, 4))
        plt.plot(x, y, label=f'y = {m}x + {b}')
        plt.scatter([x1, x2], [y1, y2], color='red')
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.grid(color='gray', linestyle='--', linewidth=0.5)
        plt.title('نمودار خط از دو نقطه')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.legend()
        plt.show()
    except Exception as e:
        messagebox.showerror("خطا", "لطفاً مختصات معتبر به فرم x,y وارد کنید")

def calculate_slope_intercept():
    try:
        x1, y1 = map(float, entry_x1.get().split(","))
        x2, y2 = map(float, entry_x2.get().split(","))

        if x1 == x2:
            messagebox.showerror("خطا", "نقاط باید دارای مقادیر x متفاوت باشند.")
            return

        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1

        messagebox.showinfo("نتیجه", f"شیب (m): {m}\nعرض از مبدا (b): {b}")
    except Exception as e:
        messagebox.showerror("خطا", "لطفاً مختصات معتبر به فرم x,y وارد کنید")

def calculate_from_equation():
    equation = entry.get()
    try:
        m, b = parse_equation(equation)
        messagebox.showinfo("نتیجه", f"شیب (m): {m}\nعرض از مبدا (b): {b}")
    except Exception as e:
        messagebox.showerror("خطا", "لطفاً یک معادله خطی معتبر به فرم y=mx+b وارد کنید")

root = tk.Tk()
root.title("رسم معادله خطی")

style = ttk.Style()
style.configure("TLabel", font=("B Nazanin", 12))
style.configure("TButton", font=("B Nazanin", 12))
style.configure("TEntry", font=("B Nazanin", 12))

label = ttk.Label(root, text="یک معادله خطی وارد کنید (y=mx+b):")
label.pack(pady=10)
entry = ttk.Entry(root, width=30)
entry.pack(pady=5)

plot_button = ttk.Button(root, text="رسم خط", command=lines)
plot_button.pack(pady=10)

label_points = ttk.Label(root, text="دو نقطه وارد کنید (x1,y1 و x2,y2):")
label_points.pack(pady=10)

entry_x1 = ttk.Entry(root, width=15)
entry_x1.pack(pady=5)
entry_x1.insert(0, "x1,y1")

entry_x2 = ttk.Entry(root, width=15)
entry_x2.pack(pady=5)
entry_x2.insert(0, "x2,y2")

plot_points_button = ttk.Button(root, text="رسم خط از نقاط", command=plot_line_from_points)
plot_points_button.pack(pady=10)

calculate_button = ttk.Button(root, text="محاسبه شیب و عرض از مبدا", command=calculate_slope_intercept)
calculate_button.pack(pady=10)

calculate_from_equation_button = ttk.Button(root, text="محاسبه از معادله", command=calculate_from_equation)
calculate_from_equation_button.pack(pady=10)

root.mainloop()