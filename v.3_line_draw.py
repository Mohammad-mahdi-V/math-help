import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk



class LineAlgorithm:
    def __init__(self):
        self.x, self.y = sp.symbols('x y')

    def parse_equation(self, equation):
        equation = equation.replace('^', '**')
        transformations = standard_transformations + (implicit_multiplication_application,)
        try:
            if "=" in equation:
                left_str, right_str = equation.split("=")
                left_expr = parse_expr(left_str, transformations=transformations)
                right_expr = parse_expr(right_str, transformations=transformations)
                expr = left_expr - right_expr
            else:
                expr = parse_expr(equation, transformations=transformations)

            solutions = sp.solve(expr, self.y)
            if solutions:
                if len(solutions) == 1:
                    sol = solutions[0]
                    m = sol.coeff(self.x)
                    b = sol.subs(self.x, 0)
                    if sp.simplify(sol - (m * self.x + b)) == 0:
                        distance = abs(b) / sp.sqrt(m ** 2 + 1)
                        distance = float(distance)
                        info = f"شیب = {float(m):.2f}، عرض از مبدا = {float(b):.2f}، فاصله از مبدا = {distance:.2f}"
                        return ("linear", sol, m, b, info)
                    else:
                        info = f"معادله منحنی: y = {sp.pretty(sol)}"
                        return ("curve", sol, None, None, info)
                else:
                    info = "معادله دارای چند شاخه است:\n"
                    for sol in solutions:
                        sol_str = sp.pretty(sol)
                        info += f"y = {sol_str}\n"
                    return ("multiple", solutions, None, None, info)
            else:
                return ("none", None, None, None, "معادله قابل حل نیست.")
        except Exception as e:
            print("Error in parse_equation:", e)
            return ("error", None, None, None, "خطا در تبدیل معادله.")

    def plot_equation(self, equation):
        eq_type, sol, m, b, info = self.parse_equation(equation)
        if eq_type == "linear":
            func = sp.lambdify(self.x, sol, 'numpy')
            x_vals = np.linspace(-20, 20, 400)
            y_vals = func(x_vals)
            plt.figure(figsize=(6, 4))
            plt.plot(x_vals, y_vals, label=f'y = {float(m):.2f}x + {float(b):.2f}')
            plt.axhline(0, color='black', linewidth=0.5)
            plt.axvline(0, color='black', linewidth=0.5)
            plt.grid(True, linestyle='--', linewidth=0.5)
            plt.title('نمودار خطی')
            plt.xlabel('x')
            plt.ylabel('y')
            plt.legend()
            plt.show()
        elif eq_type == "curve":
            func = sp.lambdify(self.x, sol, 'numpy')
            x_vals = np.linspace(-20, 20, 400)
            y_vals = func(x_vals)
            plt.figure(figsize=(6, 4))
            plt.plot(x_vals, y_vals, label=f'y = {sp.pretty(sol)}')
            plt.axhline(0, color='black', linewidth=0.5)
            plt.axvline(0, color='black', linewidth=0.5)
            plt.grid(True, linestyle='--', linewidth=0.5)
            plt.title('نمودار منحنی')
            plt.xlabel('x')
            plt.ylabel('y')
            plt.legend()
            plt.show()
        elif eq_type == "multiple":
            plt.figure(figsize=(6, 4))
            for sol_item in sol:
                sol_str = sp.pretty(sol_item)
                try:
                    func = sp.lambdify(self.x, sol_item, 'numpy')
                    x_vals = np.linspace(-20, 20, 400)
                    y_vals = func(x_vals)
                    plt.plot(x_vals, y_vals, label=f'y = {sol_str}')
                except Exception as e:
                    print(e)
            plt.axhline(0, color='black', linewidth=0.5)
            plt.axvline(0, color='black', linewidth=0.5)
            plt.grid(True, linestyle='--', linewidth=0.5)
            plt.title('نمودار منحنی')
            plt.xlabel('x')
            plt.ylabel('y')
            plt.legend()
            plt.show()
        return info

    def calculate_from_points(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        if x1 == x2:
            raise ValueError("نقاط باید دارای مقادیر x متفاوت باشند.")
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1
        return m, b

    def plot_line_from_points(self, m, b):
        distance = abs(b) / sp.sqrt(m ** 2 + 1)
        distance = float(distance)
        x_vals = np.linspace(-20, 20, 400)
        y_vals = m * x_vals + b
        plt.figure(figsize=(6, 4))
        plt.plot(x_vals, y_vals, label=f'y = {m:.2f}x + {b:.2f}')
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.grid(True, linestyle='--', linewidth=0.5)
        plt.title('نمودار خطی')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.legend()
        plt.show()
        return f"شیب = {m:.2f}، عرض از مبدا = {b:.2f}، فاصله از مبدا = {distance:.2f}"

root = tk.Tk()
root.title("رسم معادله خطی و منحنی")
style = ttk.Style()
style.configure("TLabel", font=("B Nazanin", 12))
style.configure("TButton", font=("B Nazanin", 12))
style.configure("TEntry", font=("B Nazanin", 12))

calculator = LineAlgorithm()

info_label = ttk.Label(root, text="اطلاعات معادله: ", font=("B Nazanin", 12))
info_label.pack(pady=5)

label_eq = ttk.Label(root, text="یک معادله وارد کنید:")
label_eq.pack(pady=10)
entry_eq = ttk.Entry(root, width=30)
entry_eq.pack(pady=5)

def draw_equation():
    eq = entry_eq.get()
    info = calculator.plot_equation(eq)
    info_label.config(text="اطلاعات معادله: " + info)

plot_eq_button = ttk.Button(root, text="رسم معادله", command=draw_equation)
plot_eq_button.pack(pady=10)

label_points = ttk.Label(root, text="دو نقطه وارد کنید (به صورت x,y):")
label_points.pack(pady=10)
entry_x1 = ttk.Entry(root, width=15)
entry_x1.pack(pady=5)
entry_x2 = ttk.Entry(root, width=15)
entry_x2.pack(pady=5)

def draw_line_from_points():
    try:
        point1 = tuple(map(float, entry_x1.get().split(",")))
        point2 = tuple(map(float, entry_x2.get().split(",")))
        m, b = calculator.calculate_from_points(point1, point2)
        info = calculator.plot_line_from_points(m, b)
        info_label.config(text="اطلاعات معادله: " + info)
    except Exception:
        messagebox.showerror("خطا", "مختصات نامعتبر است")

plot_points_button = ttk.Button(root, text="رسم خط از نقاط", command=draw_line_from_points)
plot_points_button.pack(pady=10)

root.mainloop()
