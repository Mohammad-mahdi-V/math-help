import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import matplotlib.pyplot as plt
import numpy as np
import string

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

            std_expr = sp.expand(expr)
            entered_form = sp.pretty(std_expr) + " = 0"

            solutions = sp.solve(expr, self.y)
            if solutions:
                if len(solutions) == 1:
                    sol = solutions[0]
                    m = sol.coeff(self.x)
                    b = sol.subs(self.x, 0)
                    if sp.simplify(sol - (m * self.x + b)) == 0:
                        distance = abs(b) / sp.sqrt(m ** 2 + 1)
                        distance = float(distance)
                        computed_form = f"y = {float(m):.2f}x + {float(b):.2f}"
                        info = (f"شیب = {float(m):.2f}، عرض = {float(b):.2f}، طول = {distance:.2f}\n"
                                f"حالت استاندارد معادله وارد شده: {entered_form}\n"
                                f"حالت استاندارد معادله: {computed_form}")
                        return ("linear", sol, m, b, info)
                    else:
                        computed_form = f"y = {sp.pretty(sol)}"
                        info = (f"معادله منحنی: {sp.pretty(sol)}\n"
                                f"حالت استاندارد معادله وارد شده: {entered_form}\n"
                                f"حالت استاندارد معادله: {computed_form}")
                        return ("curve", sol, None, None, info)
                else:
                    info = "معادله دارای چند شاخه است:\n"
                    for sol in solutions:
                        sol_str = sp.pretty(sol)
                        info += f"y = {sol_str}\n"
                    info += f"حالت استاندارد معادله وارد شده: {entered_form}"
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
        info = (f"شیب = {m:.2f}، عرض = {b:.2f}، طول = {distance:.2f}\n"
                f"حالت استاندارد معادله: y = {m:.2f}x + {b:.2f}  (یا {m:.2f}x - y + {b:.2f} = 0)")
        return info


if __name__ == '__main__':
    la = LineAlgorithm()
    eq = "3x = -2y - 7"
    result = la.parse_equation(eq)
    print("نتیجه معادله:", result[4])
calculator = LineAlgorithm()

registered_lines = []

root = tk.Tk()
root.title("رسم چند خط و نقاط تقاطع")
root.geometry("1200x800")
style = ttk.Style()
style.configure("TLabel", font=("B Nazanin", 12))
style.configure("TButton", font=("B Nazanin", 12))
style.configure("TEntry", font=("B Nazanin", 12))

info_label = ttk.Label(root, text="خطوط ثبت شده:\n", font=("B Nazanin", 12))
info_label.pack(pady=5)

label_eq_title = ttk.Label(root, text="ثبت خط از معادله", font=("B Nazanin", 14, "bold"))
label_eq_title.pack(pady=5)

label_line_name = ttk.Label(root, text="نام خط (فقط یک حرف انگلیسی):", font=("B Nazanin", 12))
label_line_name.pack(pady=5)
entry_line_name = ttk.Entry(root, width=30)
entry_line_name.pack(pady=5)

label_eq = ttk.Label(root, text="معادله خطی وارد کنید:", font=("B Nazanin", 12))
label_eq.pack(pady=10)
entry_eq = ttk.Entry(root, width=30)
entry_eq.pack(pady=5)


def register_line_from_equation():
    line_name = entry_line_name.get().strip()
    if len(line_name) != 1 or line_name not in string.ascii_letters:
        messagebox.showerror("خطا", "نام خط باید تنها یک حرف انگلیسی باشد (مثلاً A).")
        return
    if not line_name.isupper():
        messagebox.showwarning("توجه", "نام خط به حروف بزرگ تبدیل شد.")
        line_name = line_name.upper()
    for line in registered_lines:
        if line["name"] == line_name:
            messagebox.showerror("خطا", "نام خط تکراری است.")
            return
    eq = entry_eq.get().strip()
    if not eq:
        messagebox.showerror("خطا", "لطفاً معادله را وارد کنید.")
        return
    result = calculator.parse_equation(eq)
    eq_type, sol, m, b, info = result
    if eq_type != "linear":
        messagebox.showerror("خطا", "فقط معادلات خطی قابل ثبت هستند.")
        return
    registered_lines.append({"name": line_name, "m": float(m), "b": float(b), "info": info})
    update_info_label()
    entry_line_name.delete(0, tk.END)
    entry_eq.delete(0, tk.END)


register_eq_button = ttk.Button(root, text="ثبت خط از معادله", command=register_line_from_equation)
register_eq_button.pack(pady=10)

label_points_title = ttk.Label(root, text="ثبت خط از نقاط", font=("B Nazanin", 14, "bold"))
label_points_title.pack(pady=15)

label_line_name_points = ttk.Label(root, text="نام خط (فقط یک حرف انگلیسی):", font=("B Nazanin", 12))
label_line_name_points.pack(pady=5)
entry_line_name_points = ttk.Entry(root, width=30)
entry_line_name_points.pack(pady=5)

label_point1 = ttk.Label(root, text="نقطه اول (به صورت x,y):", font=("B Nazanin", 12))
label_point1.pack(pady=5)
entry_point1 = ttk.Entry(root, width=20)
entry_point1.pack(pady=5)

label_point2 = ttk.Label(root, text="نقطه دوم (به صورت x,y):", font=("B Nazanin", 12))
label_point2.pack(pady=5)
entry_point2 = ttk.Entry(root, width=20)
entry_point2.pack(pady=5)


def register_line_from_points():
    line_name = entry_line_name_points.get().strip()
    if len(line_name) != 1 or line_name not in string.ascii_letters:
        messagebox.showerror("خطا", "نام خط باید تنها یک حرف انگلیسی باشد (مثلاً A).")
        return
    if not line_name.isupper():
        messagebox.showwarning("توجه", "نام خط به حروف بزرگ تبدیل شد.")
        line_name = line_name.upper()
    for line in registered_lines:
        if line["name"] == line_name:
            messagebox.showerror("خطا", "نام خط تکراری است.")
            return
    pt1_str = entry_point1.get().strip()
    pt2_str = entry_point2.get().strip()
    if not pt1_str or not pt2_str:
        messagebox.showerror("خطا", "لطفاً هر دو نقطه را وارد کنید.")
        return
    try:
        point1 = tuple(map(float, pt1_str.split(",")))
        point2 = tuple(map(float, pt2_str.split(",")))
    except Exception:
        messagebox.showerror("خطا", "فرمت نقاط اشتباه است. به صورت x,y وارد کنید.")
        return
    try:
        m, b = calculator.calculate_from_points(point1, point2)
    except Exception as e:
        messagebox.showerror("خطا", str(e))
        return
    distance = abs(b) / np.sqrt(m ** 2 + 1)
    computed_form = f"y = {m:.2f}x + {b:.2f}"
    info = (f"شیب = {m:.2f}، عرض = {b:.2f}، طول = {distance:.2f}\n"
            f"حالت استاندارد معادله: {computed_form} (یا {m:.2f}x - y + {b:.2f} = 0)")
    registered_lines.append({"name": line_name, "m": float(m), "b": float(b), "info": info})
    update_info_label()
    entry_line_name_points.delete(0, tk.END)
    entry_point1.delete(0, tk.END)
    entry_point2.delete(0, tk.END)


register_points_button = ttk.Button(root, text="ثبت خط از نقاط", command=register_line_from_points)
register_points_button.pack(pady=10)


def update_info_label():
    info_text = "خطوط ثبت شده:\n"
    for line in registered_lines:
        info_text += f"{line['name']}: y = {line['m']:.2f}x + {line['b']:.2f}\n"
    info_label.config(text=info_text)


def plot_all_lines():
    if not registered_lines:
        messagebox.showerror("خطا", "هیچ خطی ثبت نشده است.")
        return
    plt.figure(figsize=(10, 8))
    x_vals = np.linspace(-20, 20, 400)
    intersections = []
    letter_index = 0
    for line in registered_lines:
        m = line["m"]
        b = line["b"]
        y_vals = m * x_vals + b
        plt.plot(x_vals, y_vals, label=f"{line['name']}: y = {m:.2f}x + {b:.2f}")
        distance = abs(b) / np.sqrt(m ** 2 + 1)
        x0 = -18
        y0 = m * x0 + b
        sf_text = (f"SF: {m:.2f}x - y + {b:.2f} = 0\n"
                   f"شیب: {m:.2f}\n"
                   f"عرض: {b:.2f}\n"
                   f"طول: {distance:.2f}")
        plt.annotate(sf_text, (x0, y0), textcoords="offset points", xytext=(0, -30),
                     fontsize=9, color='blue')

    n = len(registered_lines)
    for i in range(n):
        for j in range(i + 1, n):
            m1 = registered_lines[i]["m"]
            b1 = registered_lines[i]["b"]
            m2 = registered_lines[j]["m"]
            b2 = registered_lines[j]["b"]
            if abs(m1 - m2) > 1e-9:
                x_int = (b2 - b1) / (m1 - m2)
                y_int = m1 * x_int + b1
                letter = chr(ord('a') + letter_index)
                letter_index += 1
                intersections.append({"letter": letter,
                                      "line1": registered_lines[i]["name"],
                                      "line2": registered_lines[j]["name"],
                                      "x": x_int,
                                      "y": y_int})
                plt.plot(x_int, y_int, 'ro')
                plt.annotate(letter, (x_int, y_int),
                             textcoords="offset points", xytext=(5, 5),
                             color='red', fontsize=10)
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("رسم همه خطوط و نقاط تقاطع")
    plt.legend()
    intersection_details = "مشخصات نقاط تقاطع:\n"
    if intersections:
        for inter in intersections:
            intersection_details += (f"{inter['letter']}: ({inter['x']:.2f}, {inter['y']:.2f}) - "
                                     f"{inter['line1']} & {inter['line2']}\n")
    else:
        intersection_details += "هیچ نقطه تقاطعی یافت نشد."
    plt.figtext(0.5, 0.01, intersection_details, wrap=True, ha="center", fontsize=10)
    plt.show()

    update_info_label()


plot_all_lines_button = ttk.Button(root, text="رسم همه خطوط", command=plot_all_lines)
plot_all_lines_button.pack(pady=10)

root.mainloop()
