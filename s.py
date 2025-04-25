import streamlit as st
import base64
import time
import threading
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import venn
from itertools import combinations
from more_itertools.more import set_partitions
import os 
import string
import pandas as pd
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from matplotlib.ticker import MultipleLocator
import pandas as pd
from google.generativeai.generative_models import GenerativeModel
from google.generativeai.client import configure
import re
import sympy as sp
import numpy as np
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from io import BytesIO
import pickle

class LineAlgorithm:
    def __init__(self):
        self.x, self.y = sp.symbols('x y')
    # در این تابع ما اختلاف بین  درجه چند جمله ایی نسبت به ایکس  و نبست به وای را بدست می اوریم
    # با این کار از ارور مثپلات جلوگیری میکنیم
    def check_powers(self, expr):
        """بررسی توان‌های x و y در معادله ضمنی"""
        terms = expr.as_ordered_terms()
        degree_x_main=0
        degree_y_main=0
        for term in terms:
            degree_x = sp.degree(term, self.x)
            degree_y = sp.degree(term, self.y)
            # ذخیره بزرگترین
            if degree_x>degree_x_main:
                degree_x_main=degree_x
            if  degree_y>degree_y_main:
                degree_y_main=degree_y
        if abs(degree_x_main-degree_y_main)>2:
            return True
        return False
    #  در این تابع اطلعاتی درمورد خط بدست میاریم
    # تمامی طالعات لازم نبوده و برای استفاده به صورت جدا از برنامه بهینه شده است
    def parse_equation(self, equation):
            original_eq = equation.strip()
            # ایجاد شکل قابل درک معادله برای سیم پای
            eq_processed = original_eq.replace('^', '**')
            transformations = standard_transformations + (implicit_multiplication_application,)
            try:
                
                if "=" in eq_processed:
                    left_str, right_str = eq_processed.split("=")
                    left_expr = parse_expr(left_str, transformations=transformations, local_dict={'x': self.x, 'y': self.y})
                    right_expr = parse_expr(right_str, transformations=transformations, local_dict={'x': self.x, 'y': self.y})
                    expr = sp.simplify(left_expr - right_expr)
                else:
                    expr = parse_expr(eq_processed, transformations=transformations, local_dict={'x': self.x, 'y': self.y})

                #  بررسی متغیر های موجود
                allowed = {self.x, self.y}
                extra_symbols = [str(sym) for sym in expr.free_symbols if sym not in allowed]
                if extra_symbols:
                    error_msg = "متغیر(های) غیرمجاز در معادله: " + ", ".join(extra_symbols)
                    return ("error", None, None, None, error_msg)

                if self.check_powers(expr):
                    return ("error", None, None, None, "اختلاف توان‌های x و y بیشتر از دو است.")
                #  تشخیص نوع معادله
                sol_y = sp.solve(expr, self.y)
                if sol_y:
                    if len(sol_y) > 1:
                        info = "معادله دارای چند جواب است: " + ", ".join([sp.pretty(s) for s in sol_y])
                        return ("implicit_multiple", sol_y, None, None, info)
                    sol = sol_y[0]
                    try:
                        deg = sp.degree(sol, self.x)
                    except Exception:
                        deg = None
                    if deg == 1:
                        m = sp.simplify(sol.coeff(self.x))
                        b = sp.simplify(sol.subs(self.x, 0))
                        if sp.simplify(sol - (m * self.x + b)) == 0:
                            distance = abs(b) / sp.sqrt(m**2 + 1)
                            info = f"شیب = {float(m):.2f}، عرض = {float(b):.2f}، فاصله = {float(distance):.2f}"
                            return ("linear", sol, m, b, info)
                        else:
                            info = f"معادله منحنی: y = {sp.pretty(sol)}"
                            return ("curve", sol, None, None, info)
                    elif deg == 2:
                        info = f"معادله چندجمله‌ای: y = {sp.pretty(sol)}"
                        return ("parabolic", sol, None, None, info)
                    else:
                        info = f"معادله منحنی: y = {sp.pretty(sol)}"
                        return ("curve", sol, None, None, info)
                else:
                    sol_x = sp.solve(expr, self.x)
                    if sol_x:
                        sol = sol_x[0]
                        try:
                            deg = sp.degree(sol, self.y)
                        except Exception:
                            deg = None
                        if deg == 1:
                            info = f"x = {sp.pretty(sol)}"
                            return ("implicit_x", sol, None, None, info)
                        else:
                            info = f"معادله منحنی (حل نسبت به x): x = {sp.pretty(sol)}"
                            return ("curve", sol, None, None, info)
                    else:
                        info = f"معادله ضمنی: {sp.pretty(expr)} = 0"
                        return ("implicit", expr, None, None, info)
            
            except Exception as e:
                return ("error", None, None, None, f"  در تبدیل معادله در صورت مشکل ادامه دار بود با ایمیل ما در ارتباط باشید در اسرع وقت رسیدگی میشود. {e} " )

    def calculate_domain(self, expr, var, default_range=10, margin=5):
        try:
            degree = sp.degree(expr, var)
            if degree > 0:
                scale = 2 ** degree if degree > 1 else 1
                initial_range = min(default_range * scale, 20)
            else:
                initial_range = default_range

            if var == self.x:
                sol = sp.solve(expr, self.x)
            else:
                sol = sp.solve(expr, self.y)
            real_sols = [float(s) for s in sol if s.is_real and s.is_finite]
            if real_sols:
                min_val = min(real_sols) - margin
                max_val = max(real_sols) + margin
                return float(min(min_val, -initial_range)), float(max(max_val, initial_range))

            deriv = sp.diff(expr, var)
            critical_points = sp.solve(deriv, var)
            real_critical = [float(p) for p in critical_points if p.is_real and p.is_finite]
            if real_critical:
                min_val = min(real_critical) - margin
                max_val = max(real_critical) + margin
                return float(min(min_val, -initial_range)), float(max(max_val, initial_range))

            test_points =[np.linspace(-initial_range, initial_range, 50)]
            values = []
            for p in test_points:
                try:
                    if var == self.x:
                        val = float(expr.subs({self.x: p, self.y: 0}))
                    else:
                        val = float(expr.subs({self.x: 0, self.y: p}))
                    if np.isfinite(val):
                        values.append(p)
                except:
                    continue
            if values:
                min_val = min(values) - margin
                max_val = max(values) + margin
                return float(min(min_val, -initial_range)), float(max(max_val, initial_range))

            return float(-initial_range), float(initial_range)
        except Exception as e:
            print(f"Error in calculate_domain: {e}")
            return float(-initial_range), float(initial_range)

    def plot(self, equations):
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.grid(which='major', linestyle='-', linewidth=0.75)
        ax.grid(which='minor', linestyle=':', linewidth=0.5)
        intersections = []
        letter_index = 0
        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

        x_min, x_max = float('inf'), float('-inf')
        y_min, y_max = float('inf'), float('-inf')

        for line in equations:
            expr_str = line["input"].replace('^', '**')
            transformations = standard_transformations + (implicit_multiplication_application,)
            if "=" in expr_str:
                left_str, right_str = expr_str.split("=", 1)
                left_expr = parse_expr(left_str, transformations=transformations, local_dict={'x': self.x, 'y': self.y})
                right_expr = parse_expr(right_str, transformations=transformations, local_dict={'x': self.x, 'y': self.y})
                expr = sp.simplify(left_expr - right_expr)
            else:
                expr = parse_expr(expr_str, transformations=transformations, local_dict={'x': self.x, 'y': self.y})

            x_min_line, x_max_line = self.calculate_domain(expr, self.x)
            y_min_line, y_max_line = self.calculate_domain(expr, self.y)
            print(f"Line {line['name']}: x_domain = [{x_min_line}, {x_max_line}], y_domain = [{y_min_line}, {y_max_line}]")
            x_min = min(x_min, x_min_line)
            x_max = max(x_max, x_max_line)
            y_min = min(y_min, y_min_line)
            y_max = max(y_max, y_max_line)

        print(f"Final domain: x = [{x_min}, {x_max}], y = [{y_min}, {y_max}]")

        if not all(isinstance(v, (int, float)) for v in [x_min, x_max, y_min, y_max]):
            raise ValueError(f"Invalid domain values: x_min={x_min}, x_max={x_max}, y_min={y_min}, y_max={y_max}")

        x_vals = np.linspace(x_min, x_max, 400)
        y_vals_grid, x_vals_grid = np.ogrid[y_min:y_max:200j, x_min:x_max:200j]

        for i, line in enumerate(equations):
            if line.get("type", "linear") in ["general", "quadratic"]:
                if line["type"] == "general":
                    a = line["a"]
                    b_coef = line["b_coef"]
                    c = line["c"]
                    if b_coef != 0:
                        m_line = -a / b_coef
                        intercept = -c / b_coef
                        y_vals = m_line * x_vals + intercept
                        ax.plot(x_vals, y_vals, label=f"{line['name']}: y = {m_line:.2f}x + {intercept:.2f}")
                    else:
                        x_vert = -c / a
                        ax.axvline(x=x_vert, color='blue', label=f"{line['name']}: x = {x_vert:.2f}")
                else:
                    a = line["a"]
                    b_coef = line["b_coef"]
                    c = line["c"]
                    func = sp.lambdify(self.x, a * self.x**2 + b_coef * self.x + c, 'numpy')
                    y_vals = func(x_vals)
                    ax.plot(x_vals, y_vals, label=f"{line['name']}: {a}x² + {b_coef}x + {c}")

            elif line["type"] == "implicit" or line["type"] == "parabolic":
                expr = line["input"].replace('^', '**')
                transformations = standard_transformations + (implicit_multiplication_application,)
                if "=" in expr:
                    left_str, right_str = expr.split("=", 1)
                    left_expr = parse_expr(left_str, transformations=transformations, local_dict={'x': self.x, 'y': self.y})
                    right_expr = parse_expr(right_str, transformations=transformations, local_dict={'x': self.x, 'y': self.y})
                    expr = sp.simplify(left_expr - right_expr)
                else:
                    expr = parse_expr(expr, transformations=transformations, local_dict={'x': self.x, 'y': self.y})
                f = sp.lambdify((self.x, self.y), expr, 'numpy')
                color = colors[i % len(colors)]
                ax.contour(x_vals_grid.ravel(), y_vals_grid.ravel(), f(x_vals_grid, y_vals_grid), [0], colors=color)
                ax.plot([], [], color=color, label=f"{line['name']}: {line['input']}")

            elif line["type"] == "implicit_multiple":
                expr_str = line["input"].replace('^', '**')
                transformations = standard_transformations + (implicit_multiplication_application,)
                left_str, right_str = expr_str.split("=", 1)
                left_expr = parse_expr(left_str, transformations=transformations, local_dict={'x': self.x, 'y': self.y})
                right_expr = parse_expr(right_str, transformations=transformations, local_dict={'x': self.x, 'y': self.y})
                expr = sp.simplify(left_expr - right_expr)
                sol_y = sp.solve(expr, self.y)
                if sol_y:
                    n = i
                    for j, sol in enumerate(sol_y):
                        try:
                            sol_rewritten = sol.rewrite(sp.Pow)
                            func = sp.lambdify(self.x, sol, 'numpy')
                            y_vals = func(x_vals)
                            color = colors[n % len(colors)]
                            y_real = np.real_if_close(y_vals)
                            mask = np.isreal(y_real) & np.isfinite(y_real)
                            ax.plot(x_vals[mask], y_real[mask], color=color, label=f"{line['name']} - {j+1}: y = ${sp.latex(sol_rewritten)}$")
                            n += 1
                        except Exception as e:
                            st.warning(f"خطا در رسم جواب {j+1} معادله {line['name']}: {e}")

            elif line["type"] == "curve":
                expr_str = line["input"].replace('^', '**')
                transformations = standard_transformations + (implicit_multiplication_application,)
                try:
                    if "=" in expr_str:
                        left_str, right_str = expr_str.split("=", 1)
                        left_expr = parse_expr(left_str, transformations=transformations, local_dict={'x': self.x, 'y': self.y})
                        right_expr = parse_expr(right_str, transformations=transformations, local_dict={'x': self.x, 'y': self.y})
                        expr = sp.simplify(left_expr - right_expr)
                    else:
                        expr = parse_expr(expr_str, transformations=transformations, local_dict={'x': self.x, 'y': self.y})

                    sol_x = sp.solve(expr, self.x)
                    sol_y = sp.solve(expr, self.y)

                    if sol_y:
                        for j, sol in enumerate(sol_y):
                            try:
                                sol_rewritten = sol.rewrite(sp.Pow)
                                func = sp.lambdify(self.x, sol, 'numpy')
                                y_vals = func(x_vals)
                                y_real = np.real_if_close(y_vals)
                                mask = np.isreal(y_real) & np.isfinite(y_real)
                                color = colors[(i + j) % len(colors)]
                                ax.plot(x_vals[mask], y_real[mask], color=color, 
                                        label=f"{line['name']} - y{j+1}: y = ${sp.latex(sol_rewritten)}$")
                            except Exception as e:
                                st.warning(f"خطا در رسم جواب y{j+1} معادله {line['name']}: {e}")

                    if sol_x:
                        for j, sol in enumerate(sol_x):
                            try:
                                sol_rewritten = sol.rewrite(sp.Pow)
                                func = sp.lambdify(self.y, sol, 'numpy')
                                y_range = np.linspace(y_min, y_max, 400)
                                x_vals_sol = func(y_range)
                                x_real = np.real_if_close(x_vals_sol)
                                mask = np.isreal(x_real) & np.isfinite(x_real)
                                color = colors[(i + j) % len(colors)]
                                ax.plot(x_real[mask], y_range[mask], color=color, 
                                        label=f"{line['name']} - x{j+1}: x = ${sp.latex(sol_rewritten)}$")
                            except Exception as e:
                                st.warning(f"خطا در رسم جواب x{j+1} معادله {line['name']}: {e}")

                    f = sp.lambdify((self.x, self.y), expr, 'numpy')
                    color = colors[i % len(colors)]
                    ax.contour(x_vals_grid.ravel(), y_vals_grid.ravel(), f(x_vals_grid, y_vals_grid), [0], colors=color, linestyles='dashed')
                    ax.plot([], [], color=color, linestyle='dashed', label=f"{line['name']} (ضمنی): {line['input']}")

                except Exception as e:
                    st.error(f"خطا در رسم معادله {line['name']}: {str(e)}")

            else:
                m_line = line.get("m", None)
                b_line = line.get("b", None)
                if m_line is None or b_line is None:
                    expr_str = line["input"].replace('^', '**')
                    if expr_str.lower().startswith("y="):
                        expr_str = expr_str[2:]
                    try:
                        func = sp.lambdify(self.x, sp.sympify(expr_str, locals={'x': self.x, 'y': self.y}), 'numpy')
                        y_vals = func(x_vals)
                        ax.plot(x_vals, y_vals, label=f"{line['name']}: {line['input']}")
                    except Exception as e:
                        try:
                            if "=" in expr_str:
                                left_str, right_str = expr_str.split("=", 1)
                                expr = sp.sympify(right_str, locals={'x': self.x, 'y': self.y}) - sp.sympify(left_str, locals={'x': self.x, 'y': self.y})
                                sol_y = sp.solve(expr, self.y)
                                if sol_y:
                                    for j, sol in enumerate(sol_y):
                                        sol_rewritten = sol.rewrite(sp.Pow)
                                        func = sp.lambdify(self.x, sol, 'numpy')
                                        y_vals = func(x_vals)
                                        ax.plot(x_vals, y_vals, label=f"{line['name']} - {j+1}: y = ${sp.latex(sol_rewritten)}$")
                        except:
                            st.error(f"خطا در رسم معادله {line['name']}: {str(e)}")
                else:
                    y_vals = m_line * x_vals + b_line
                    ax.plot(x_vals, y_vals, label=f"{line['name']}: y = {m_line:.2f}x + {b_line:.2f}")

        n = len(equations)
        for i in range(n):
            for j in range(i + 1, n):
                line_i = equations[i]
                line_j = equations[j]
                try:
                    expr_str_i = line_i["input"].replace('^', '**')
                    expr_str_j = line_j["input"].replace('^', '**')
                    transformations = standard_transformations + (implicit_multiplication_application,)
                    if "=" in expr_str_i:
                        left_str_i, right_str_i = expr_str_i.split("=", 1)
                        left_expr_i = parse_expr(left_str_i, transformations=transformations, local_dict={'x': self.x, 'y': self.y})
                        right_expr_i = parse_expr(right_str_i, transformations=transformations, local_dict={'x': self.x, 'y': self.y})
                        expr_i = sp.simplify(left_expr_i - right_expr_i)
                    else:
                        expr_i = parse_expr(expr_str_i, transformations=transformations, local_dict={'x': self.x, 'y': self.y})

                    if "=" in expr_str_j:
                        left_str_j, right_str_j = expr_str_j.split("=", 1)
                        left_expr_j = parse_expr(left_str_j, transformations=transformations, local_dict={'x': self.x, 'y': self.y})
                        right_expr_j = parse_expr(right_str_j, transformations=transformations, local_dict={'x': self.x, 'y': self.y})
                        expr_j = sp.simplify(left_expr_j - right_expr_j)
                    else:
                        expr_j = parse_expr(expr_str_j, transformations=transformations, local_dict={'x': self.x, 'y': self.y})

                    solutions = sp.solve([expr_i, expr_j], (self.x, self.y), dict=True)
                    for sol in solutions:
                        x_int = float(sol[self.x])
                        y_int = float(sol[self.y])
                        if x_min <= x_int <= x_max and y_min <= y_int <= y_max:
                            letter = chr(ord('a') + letter_index)
                            letter_index += 1
                            intersections.append({
                                "letter": letter,
                                "line1": line_i["name"],
                                "line2": line_j["name"],
                                "x": x_int,
                                "y": y_int
                            })
                            ax.plot(x_int, y_int, 'ro')
                            ax.annotate(letter, (x_int, y_int), textcoords="offset points", xytext=(5, 5),
                                        color='red', fontsize=10)
                except Exception as e:
                    try:
                        def f(xy):
                            x_val, y_val = xy
                            return [
                                float(expr_i.subs({self.x: x_val, self.y: y_val})),
                                float(expr_j.subs({self.x: x_val, self.y: y_val}))
                            ]
                        x_guess = (x_min + x_max) / 2
                        y_guess = (y_min + y_max) / 2
                        sol = sp.nsolve([expr_i, expr_j], [self.x, self.y], [x_guess, y_guess])
                        x_int, y_int = float(sol[0]), float(sol[1])
                        if x_min <= x_int <= x_max and y_min <= y_int <= y_max:
                            letter = chr(ord('a') + letter_index)
                            letter_index += 1
                            intersections.append({
                                "letter": letter,
                                "line1": line_i["name"],
                                "line2": line_j["name"],
                                "x": x_int,
                                "y": y_int
                            })
                            ax.plot(x_int, y_int, 'ro')
                            ax.annotate(letter, (x_int, y_int), textcoords="offset points", xytext=(5, 5),
                                        color='red', fontsize=10)
                    except Exception as e:
                        st.warning(f"خطا در محاسبه تقاطع بین {line_i['name']} و {line_j['name']}: {e}")

        ax.axhline(0, color='black', linewidth=0.5)
        ax.axvline(0, color='black', linewidth=0.5)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.legend(fontsize='small', loc='best')
        return fig
    def calculate_from_points(self, point1, point2):
        # ایجاد معادله از روی نقطه
        x1, y1 = point1
        x2, y2 = point2
        if x1 == x2:
            raise ValueError("مقادیر x نقاط نباید برابر باشند.")
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1
        return m, b
    

line_algo = LineAlgorithm()
result = line_algo.parse_equation("x^4 + y^6 + y = 10")
print(result)