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


transformations = standard_transformations + (implicit_multiplication_application,)
def barkhord():
    def parse_equation(equation):
        """
        این تابع معادله ورودی را می‌گیرد و سعی می‌کند آن را به فرم y = m*x + b تبدیل کند.
        از تابع parse_expr با تبدیل ضرب ضمنی استفاده می‌کند تا ورودی‌هایی مانند 2y به 2*y تبدیل شوند.
        """
        x, y = sp.symbols('x y')
        try:
            if '=' in equation:
                parts = equation.split('=')
                if len(parts) != 2:
                    raise ValueError("معادله باید شامل یک علامت = باشد.")
                lhs = parts[0].strip()
                rhs = parts[1].strip()
                # استفاده از parse_expr به همراه تنظیمات تبدیل ضرب ضمنی
                lhs_expr = parse_expr(lhs, transformations=transformations)
                rhs_expr = parse_expr(rhs, transformations=transformations)
                eq = sp.Eq(lhs_expr, rhs_expr)
            else:
                # اگر علامت = وجود نداشته باشد، فرض می‌کنیم معادله به عنوان عبارت برای y داده شده است.
                eq = sp.Eq(y, parse_expr(equation, transformations=transformations))
                
            # حل معادله برای y
            sol = sp.solve(eq, y)
            if not sol:
                # در صورتی که y به صورت صریح در معادله وجود نداشته باشد
                expr = parse_expr(equation, transformations=transformations)
                A = expr.coeff(x)
                B = expr.coeff(y)
                C = expr - A*x - B*y
                if B == 0:
                    raise ValueError("معادله عمودی است و قابل تبدیل به فرم y=mx+b نیست.")
                m = -A / B
                b = -C / B
                return float(m), float(b)
            sol_line = sol[0]
            # محاسبه شیب (m) با مشتق گرفتن نسبت به x
            m_expr = sp.simplify(sp.diff(sol_line, x))
            # محاسبه عرض از مبدا (b) با تفریق m*x از حل معادله
            b_expr = sp.simplify(sol_line - m_expr * x)
            return float(m_expr), float(b_expr)
        except Exception as e:
            raise ValueError("فرمت معادله نامعتبر است. لطفاً یک معادله خطی وارد کنید.")

    def get_line_from_points(point1, point2):
        """
        محاسبه شیب و عرض از مبدا از دو نقطه ورودی به فرم x,y
        """
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

    def calculate_and_plot():
        try:
            # پردازش خط اول (با توجه به حالت انتخاب شده: معادله یا نقاط)
            if line1_mode.get() == "equation":
                eq1 = entry_line1.get()
                m1, b1 = parse_equation(eq1)
            else:
                pt1 = entry_line1_point1.get()
                pt2 = entry_line1_point2.get()
                m1, b1 = get_line_from_points(pt1, pt2)
                
            # پردازش خط دوم
            if line2_mode.get() == "equation":
                eq2 = entry_line2.get()
                m2, b2 = parse_equation(eq2)
            else:
                pt3 = entry_line2_point1.get()
                pt4 = entry_line2_point2.get()
                m2, b2 = get_line_from_points(pt3, pt4)
            
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

    # ایجاد پنجره اصلی
    root = tk.Tk()
    root.title("رسم خطوط و محاسبه نقطه تقاطع")

    # -------------------------- بخش ورودی خط اول --------------------------
    frame_line1 = ttk.LabelFrame(root, text="خط اول", padding=10)
    frame_line1.pack(padx=10, pady=10, fill="both", expand=True)

    # انتخاب حالت ورودی: معادله یا نقطه‌ای
    line1_mode = tk.StringVar(value="equation")
    rbtn_line1_eq = ttk.Radiobutton(frame_line1, text="معادله", variable=line1_mode, value="equation", command=lambda: update_line1_inputs())
    rbtn_line1_pts = ttk.Radiobutton(frame_line1, text="نقطه‌ای", variable=line1_mode, value="points", command=lambda: update_line1_inputs())
    rbtn_line1_eq.grid(row=0, column=0, sticky="w")
    rbtn_line1_pts.grid(row=0, column=1, sticky="w")

    # بخش ورود معادله برای خط اول
    label_line1 = ttk.Label(frame_line1, text="معادله خط اول:")
    label_line1.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
    entry_line1 = ttk.Entry(frame_line1, width=40)
    entry_line1.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

    # بخش ورود نقاط برای خط اول (دو نقطه)
    label_line1_pt1 = ttk.Label(frame_line1, text="نقطه ۱ (x,y):")
    entry_line1_point1 = ttk.Entry(frame_line1, width=20)
    label_line1_pt2 = ttk.Label(frame_line1, text="نقطه ۲ (x,y):")
    entry_line1_point2 = ttk.Entry(frame_line1, width=20)

    def update_line1_inputs():
        if line1_mode.get() == "equation":
            label_line1.grid()
            entry_line1.grid()
            label_line1_pt1.grid_remove()
            entry_line1_point1.grid_remove()
            label_line1_pt2.grid_remove()
            entry_line1_point2.grid_remove()
        else:
            label_line1.grid_remove()
            entry_line1.grid_remove()
            label_line1_pt1.grid(row=1, column=0, sticky="w", pady=5)
            entry_line1_point1.grid(row=1, column=1, sticky="w", pady=5)
            label_line1_pt2.grid(row=2, column=0, sticky="w", pady=5)
            entry_line1_point2.grid(row=2, column=1, sticky="w", pady=5)

    update_line1_inputs()  # به‌روزرسانی اولیه نمایش

    # -------------------------- بخش ورودی خط دوم --------------------------
    frame_line2 = ttk.LabelFrame(root, text="خط دوم", padding=10)
    frame_line2.pack(padx=10, pady=10, fill="both", expand=True)

    # انتخاب حالت ورودی برای خط دوم
    line2_mode = tk.StringVar(value="equation")
    rbtn_line2_eq = ttk.Radiobutton(frame_line2, text="معادله", variable=line2_mode, value="equation", command=lambda: update_line2_inputs())
    rbtn_line2_pts = ttk.Radiobutton(frame_line2, text="نقطه‌ای", variable=line2_mode, value="points", command=lambda: update_line2_inputs())
    rbtn_line2_eq.grid(row=0, column=0, sticky="w")
    rbtn_line2_pts.grid(row=0, column=1, sticky="w")

    # بخش ورود معادله برای خط دوم
    label_line2 = ttk.Label(frame_line2, text="معادله خط دوم:")
    label_line2.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
    entry_line2 = ttk.Entry(frame_line2, width=40)
    entry_line2.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

    # بخش ورود نقاط برای خط دوم (دو نقطه)
    label_line2_pt1 = ttk.Label(frame_line2, text="نقطه ۱ (x,y):")
    entry_line2_point1 = ttk.Entry(frame_line2, width=20)
    label_line2_pt2 = ttk.Label(frame_line2, text="نقطه ۲ (x,y):")
    entry_line2_point2 = ttk.Entry(frame_line2, width=20)

    def update_line2_inputs():
        if line2_mode.get() == "equation":
            label_line2.grid()
            entry_line2.grid()
            label_line2_pt1.grid_remove()
            entry_line2_point1.grid_remove()
            label_line2_pt2.grid_remove()
            entry_line2_point2.grid_remove()
        else:
            label_line2.grid_remove()
            entry_line2.grid_remove()
            label_line2_pt1.grid(row=1, column=0, sticky="w", pady=5)
            entry_line2_point1.grid(row=1, column=1, sticky="w", pady=5)
            label_line2_pt2.grid(row=2, column=0, sticky="w", pady=5)
            entry_line2_point2.grid(row=2, column=1, sticky="w", pady=5)

    update_line2_inputs()  # به‌روزرسانی اولیه

    # دکمه محاسبه و رسم
    btn_calculate = ttk.Button(root, text="محاسبه و رسم", command=calculate_and_plot)
    btn_calculate.pack(pady=10)

    root.mainloop()
