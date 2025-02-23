import tkinter as tk
from tkinter import messagebox
import re
import matplotlib.pyplot as plt

# کلاس نمایش خط با تبدیل ورودی به فرمت استاندارد Ax+By+C=0
class Line:
    def __init__(self, name, input_type, input_data, color):
        self.name = name
        self.input_type = input_type  # "equation" یا "points"
        self.color = color
        if input_type == "equation":
            eq = input_data.replace(" ", "")
            if eq.startswith("y="):
                # فرمت مورد قبول: y=mx+c
                pattern = r"y=([-+]?\d*\.?\d*)x([-+]\d*\.?\d+)"
                match = re.match(pattern, eq)
                if match:
                    m_str, c_str = match.groups()
                    if m_str == "" or m_str == "+":
                        m = 1.0
                    elif m_str == "-":
                        m = -1.0
                    else:
                        m = float(m_str)
                    c = float(c_str)
                    # معادله y=mx+c معادل -m*x + y - c = 0 است.
                    self.A = -m
                    self.B = 1
                    self.C = -c
                else:
                    raise ValueError("فرمت معادله صحیح نیست. فرمت مجاز: y=mx+c")
            elif eq.startswith("x="):
                try:
                    const = float(eq[2:])
                    self.A = 1
                    self.B = 0
                    self.C = -const
                except:
                    raise ValueError("فرمت معادله صحیح نیست. فرمت مجاز: x=c")
            else:
                raise ValueError("فرمت معادله باید با y= یا x= شروع شود.")
        elif input_type == "points":
            # ورودی باید به صورت "x1,y1,x2,y2" باشد
            try:
                parts = input_data.split(',')
                if len(parts) != 4:
                    raise ValueError
                x1, y1, x2, y2 = map(float, parts)
                self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
                if x1 == x2 and y1 == y2:
                    raise ValueError("نقاط نمی‌توانند یکسان باشند.")
                # معادله از دو نقطه: (y2-y1)x - (x2-x1)y + (x2-x1)*y1 - (y2-y1)*x1 = 0
                self.A = y2 - y1
                self.B = -(x2 - x1)
                self.C = (x2 - x1)*y1 - (y2 - y1)*x1
            except:
                raise ValueError("ورودی مختصات صحیح نیست. از قالب x1,y1,x2,y2 استفاده کنید.")
        else:
            raise ValueError("نوع ورودی نامعتبر است.")

# کلاس محاسبات تقاطع خطوط
class IntersectionCalculator:
    @staticmethod
    def compute_intersection(line1, line2):
        D = line1.A * line2.B - line2.A * line1.B
        if D == 0:
            return None  # خطوط موازی یا هم‌خط هستند
        Dx = -line1.C * line2.B + line2.C * line1.B
        Dy = -line2.C * line1.A + line1.C * line2.A
        x = Dx / D
        y = Dy / D
        return (x, y)

    @staticmethod
    def compute_all_intersections(lines):
        intersections = []
        n = len(lines)
        for i in range(n):
            for j in range(i+1, n):
                pt = IntersectionCalculator.compute_intersection(lines[i], lines[j])
                if pt is not None:
                    intersections.append((pt, (lines[i].name, lines[j].name)))
        return intersections

# کلاس گرافیکی برای رسم خطوط و نقاط تقاطع با matplotlib
class MatplotlibHandler:
    def __init__(self, world_bounds=(-10, 10, -10, 10)):
        self.world_bounds = world_bounds  # (x_min, x_max, y_min, y_max)

    def get_line_segment(self, line):
        x_min, x_max, y_min, y_max = self.world_bounds
        points = []
        for x in [x_min, x_max]:
            if line.B != 0:
                y = (-line.C - line.A * x) / line.B
                if y_min <= y <= y_max:
                    points.append((x, y))
        for y in [y_min, y_max]:
            if line.A != 0:
                x = (-line.C - line.B * y) / line.A
                if x_min <= x <= x_max:
                    points.append((x, y))
        unique_points = []
        for p in points:
            if p not in unique_points:
                unique_points.append(p)
        if len(unique_points) < 2:
            return None
        return unique_points[:2]

    def draw_all(self, lines, intersections):
        fig, ax = plt.subplots()
        x_min, x_max, y_min, y_max = self.world_bounds
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_aspect('equal', adjustable='box')
        for line in lines:
            segment = self.get_line_segment(line)
            if segment:
                p1, p2 = segment
                xs = [p1[0], p2[0]]
                ys = [p1[1], p2[1]]
                ax.plot(xs, ys, color=line.color, label=line.name, linewidth=2)
        for (pt, names) in intersections:
            ax.plot(pt[0], pt[1], 'ko', markersize=6)
        ax.legend()
        ax.set_title("رسم خطوط و نقاط تقاطع")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.grid(True)
        plt.show()

# کلاس اصلی برنامه که واسط کاربری Tkinter و منطق (matplotlib) را ترکیب می‌کند
class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("محل تقاطع خطوط")
        self.lines = []
        self.colors = ["red", "green", "blue", "orange", "purple", "brown", "cyan", "magenta"]
        self.current_color_index = 0
        # وضعیت برای ورودی نقاط: مرحله 1 (نقطه اول) یا 2 (نقطه دوم)
        self.point_stage = 1
        self.first_point = None
        self.create_widgets()
        self.graphics = MatplotlibHandler(world_bounds=(-10, 10, -10, 10))

    def create_widgets(self):
        input_frame = tk.Frame(self.root)
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # انتخاب نوع ورودی
        self.input_type = tk.StringVar(value="equation")
        rb_eq = tk.Radiobutton(input_frame, text="معادله", variable=self.input_type, value="equation", command=self.update_input_mode)
        rb_points = tk.Radiobutton(input_frame, text="مختصات دو نقطه", variable=self.input_type, value="points", command=self.update_input_mode)
        rb_eq.grid(row=0, column=0, padx=5, pady=5)
        rb_points.grid(row=0, column=1, padx=5, pady=5)

        # ورودی نام خط
        tk.Label(input_frame, text="نام خط:").grid(row=1, column=0, pady=5)
        self.entry_name = tk.Entry(input_frame)
        self.entry_name.grid(row=1, column=1, pady=5)

        # برچسب و اینتری ورودی برای خط (یا نقاط)
        self.input_label = tk.Label(input_frame, text="ورودی معادله:")
        self.input_label.grid(row=2, column=0, pady=5)
        self.entry_line = tk.Entry(input_frame)
        self.entry_line.grid(row=2, column=1, pady=5)

        # دکمه ثبت خط
        self.btn_register = tk.Button(input_frame, text="ثبت خط", command=self.register_line)
        self.btn_register.grid(row=3, column=0, columnspan=2, pady=5)

        # دکمه رسم (ابتدا غیرفعال)
        self.btn_draw = tk.Button(input_frame, text="رسم", command=self.draw_lines, state="disabled")
        self.btn_draw.grid(row=4, column=0, columnspan=2, pady=5)

        # لیست خطوط ثبت‌شده
        self.listbox = tk.Listbox(self.root)
        self.listbox.pack(fill=tk.X, padx=10, pady=5)

    def update_input_mode(self):
        # تغییر برچسب و تنظیم مجدد وضعیت ورودی در صورت تغییر نوع ورودی
        mode = self.input_type.get()
        if mode == "points":
            self.input_label.config(text="نقطه اول (x,y):")
            self.entry_line.delete(0, tk.END)
            self.point_stage = 1
            self.first_point = None
        else:
            self.input_label.config(text="ورودی معادله:")
            self.entry_line.delete(0, tk.END)

    def register_line(self):
        name = self.entry_name.get().strip()
        if name == "":
            messagebox.showerror("خطا", "لطفاً نام خط را وارد کنید.")
            return
        # بررسی یگانه بودن نام خط
        for line in self.lines:
            if line.name == name:
                messagebox.showerror("خطا", "این نام قبلاً استفاده شده است.")
                return

        mode = self.input_type.get()
        color = self.colors[self.current_color_index % len(self.colors)]
        self.current_color_index += 1

        if mode == "equation":
            line_input = self.entry_line.get().strip()
            if line_input == "":
                messagebox.showerror("خطا", "ورودی خط را وارد کنید.")
                return
            try:
                new_line = Line(name, "equation", line_input, color)
            except ValueError as e:
                messagebox.showerror("خطا", str(e))
                return
            self.lines.append(new_line)
            self.listbox.insert(tk.END, f"{name} - {color}")
            self.entry_name.delete(0, tk.END)
            self.entry_line.delete(0, tk.END)
        elif mode == "points":
            point_input = self.entry_line.get().strip()
            if point_input == "":
                messagebox.showerror("خطا", "مختصات را وارد کنید (به صورت x,y).")
                return
            try:
                x_str, y_str = point_input.split(',')
                x = float(x_str.strip())
                y = float(y_str.strip())
            except:
                messagebox.showerror("خطا", "فرمت مختصات صحیح نیست. از قالب x,y استفاده کنید.")
                return

            if self.point_stage == 1:
                self.first_point = (x, y)
                self.point_stage = 2
                self.input_label.config(text="نقطه دوم (x,y):")
                self.entry_line.delete(0, tk.END)
                return  # در این مرحله خط ثبت نمی‌شود
            elif self.point_stage == 2:
                second_point = (x, y)
                # ترکیب دو نقطه به رشته مورد نیاز: x1,y1,x2,y2
                points_str = f"{self.first_point[0]},{self.first_point[1]},{second_point[0]},{second_point[1]}"
                try:
                    new_line = Line(name, "points", points_str, color)
                except ValueError as e:
                    messagebox.showerror("خطا", str(e))
                    # در صورت خطا، دوباره درخواست نقطه دوم
                    self.entry_line.delete(0, tk.END)
                    return
                self.lines.append(new_line)
                self.listbox.insert(tk.END, f"{name} - {color}")
                # بازنشانی وضعیت ورودی نقاط
                self.point_stage = 1
                self.first_point = None
                self.input_label.config(text="نقطه اول (x,y):")
                self.entry_line.delete(0, tk.END)
                self.entry_name.delete(0, tk.END)
        # فعال شدن دکمه رسم پس از ثبت حداقل دو خط
        if len(self.lines) >= 2:
            self.btn_draw.config(state="normal")

    def draw_lines(self):
        intersections = IntersectionCalculator.compute_all_intersections(self.lines)
        self.graphics.draw_all(self.lines, intersections)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
