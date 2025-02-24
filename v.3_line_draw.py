import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

class LineCalculator:
    def __init__(self):
        self.x, self.y = sp.symbols('x y')

    def parse_equation(self, equation):
        """
        معادله را به فرم y=mx+b تجزیه کرده و شیب (m) و عرض از مبدأ (b) را برمی‌گرداند.
        """
        try:
            expr = sp.sympify(equation)
            if self.y not in expr.free_symbols:
                expr = sp.Eq(self.y, expr)
            elif '=' in equation:
                lhs, rhs = equation.split('=')
                expr = sp.Eq(sp.sympify(lhs), sp.sympify(rhs))
            else:
                raise ValueError("Invalid equation format")
            solved_expr = sp.solve(expr, self.y)
            coeffs = solved_expr[0].as_coefficients_dict()
            m = sp.simplify(coeffs.get(self.x, 0))
            b = sp.simplify(coeffs.get(1, 0))
            return float(m), float(b)
        except Exception as e:
            raise ValueError("Invalid equation format")

    def calculate_from_equation(self, equation):
        """
        محاسبه شیب و عرض از مبدأ از معادله ورودی به فرم y=mx+b.
        """
        return self.parse_equation(equation)

    def calculate_from_points(self, point1, point2):
        """
        با دریافت دو نقطه (x1,y1) و (x2,y2) شیب و عرض از مبدأ خط را محاسبه می‌کند.
        """
        x1, y1 = point1
        x2, y2 = point2
        if x1 == x2:
            raise ValueError("نقاط باید دارای مقادیر x متفاوت باشند.")
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m *  x1
        return m, b

    def plot_line_from_equation(self, equation):
        """
        نمودار معادله خطی ورودی به فرم y=mx+b را رسم می‌کند.
        """
        m, b = self.parse_equation(equation)
        x = np.linspace(-20, 20, 400)
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

    def plot_line_from_points(self, point1, point2):
        """
        نمودار خط عبوری از دو نقطه ورودی را رسم می‌کند.
        """
        m, b = self.calculate_from_points(point1, point2)
        x1, y1 = point1
        x2, y2 = point2
        x = np.linspace(min(x1, x2) - 10, max(x1, x2) + 10, 400)
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


# ------------------ کد رابط گرافیکی Tkinter ------------------

root = tk.Tk()
root.title("رسم معادله خطی")

style = ttk.Style()
style.configure("TLabel", font=("B Nazanin", 12))
style.configure("TButton", font=("B Nazanin", 12))
style.configure("TEntry", font=("B Nazanin", 12))

# ایجاد یک نمونه از کلاس LineCalculator
calculator = LineCalculator()

# ورودی معادله
label = ttk.Label(root, text="یک معادله خطی وارد کنید (y=mx+b):")
label.pack(pady=10)
entry = ttk.Entry(root, width=30)
entry.pack(pady=5)

def draw_line():
    equation = entry.get()
    try:
        calculator.plot_line_from_equation(equation)
    except Exception as e:
        messagebox.showerror("خطا", "لطفاً یک معادله خطی معتبر به فرم y=mx+b وارد کنید")

plot_button = ttk.Button(root, text="رسم خط", command=draw_line)
plot_button.pack(pady=10)

# ورودی دو نقطه
label_points = ttk.Label(root, text="دو نقطه وارد کنید (x1,y1 و x2,y2):")
label_points.pack(pady=10)

entry_x1 = ttk.Entry(root, width=15)
entry_x1.pack(pady=5)
entry_x1.insert(0, "x1,y1")

entry_x2 = ttk.Entry(root, width=15)


entry_x2.pack(pady=5)
entry_x2.insert(0, "x2,y2")

def draw_line_from_points():
    try:
        point1 = tuple(map(float, entry_x1.get().split(",")))
        point2 = tuple(map(float, entry_x2.get().split(",")))
        calculator.plot_line_from_points(point1, point2)
    except Exception as e:
        messagebox.showerror("خطا", "لطفاً مختصات معتبر به فرم x,y وارد کنید")

plot_points_button = ttk.Button(root, text="رسم خط از نقاط", command=draw_line_from_points)
plot_points_button.pack(pady=10)

def show_slope_intercept():
    try:
        point1 = tuple(map(float, entry_x1.get().split(",")))
        point2 = tuple(map(float, entry_x2.get().split(",")))
        m, b = calculator.calculate_from_points(point1, point2)
        messagebox.showinfo("نتیجه", f"شیب (m): {m}\nعرض از مبدا (b): {b}")
    except Exception as e:
        messagebox.showerror("خطا", "لطفاً مختصات معتبر به فرم x,y وارد کنید")

calculate_button = ttk.Button(root, text="محاسبه شیب و عرض از مبدا", command=show_slope_intercept)
calculate_button.pack(pady=10)

def show_from_equation():
    equation = entry.get()
    try:
        m, b = calculator.calculate_from_equation(equation)
        messagebox.showinfo("نتیجه", f"شیب (m): {m}\nعرض از مبدا (b): {b}")
    except Exception as e:
        messagebox.showerror("خطا", "لطفاً یک معادله خطی معتبر به فرم y=mx+b وارد کنید")

calculate_from_equation_button = ttk.Button(root, text="محاسبه از معادله", command=show_from_equation)
calculate_from_equation_button.pack(pady=10)

root.mainloop()