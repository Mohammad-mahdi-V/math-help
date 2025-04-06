import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import string
import pandas as pd
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from streamlit_javascript import st_javascript  
from matplotlib.ticker import MultipleLocator
import base64
# ====================================
# تابع استایل‌دهی سفارشی
def setup_page():
    st.set_page_config(
        layout="wide",
        page_title="راهنمای ریاضی",
        page_icon="",
        initial_sidebar_state="expanded"
    )
    with open("data/img/bg.png", "rb") as f:
        bg = base64.b64encode(f.read()).decode("utf-8")
    with open("data/font/YekanBakhFaNum-Fat.woff2", "rb") as f:
        yekan_fat = base64.b64encode(f.read()).decode("utf-8")
    with open("data/font/YekanBakhFaNum-Bold.woff2", "rb") as f:
        yekan_bold = base64.b64encode(f.read()).decode("utf-8")
    with open("data/font/YekanBakhFaNum-Heavy.woff2", "rb") as f:
        yekan_heavy = base64.b64encode(f.read()).decode("utf-8")
    with open("data/font/YekanBakhFaNum-Light.woff2", "rb") as f:
        yekan_light = base64.b64encode(f.read()).decode("utf-8")
    with open("data/font/YekanBakhFaNum-Medium.woff2", "rb") as f:
        yekan_medium = base64.b64encode(f.read()).decode("utf-8")
    with open("data/font/YekanBakhFaNum-Regular.woff2", "rb") as f:
        yekan_regular = base64.b64encode(f.read()).decode("utf-8")

    st.markdown(f"""
    <style>
    @font-face {{
        font-family: 'YekanBakhFaNum';
        src: url(data:font/woff2;base64,{yekan_fat}) format('woff2');
        font-weight: 900;
        font-style: normal;
    }}
    @font-face {{
        font-family: 'YekanBakhFaNum';
        src: url(data:font/woff2;base64,{yekan_bold}) format('woff2');
        font-weight: bold;
        font-style: normal;
    }}
    @font-face {{
        font-family: 'YekanBakhFaNum';
        src: url(data:font/woff2;base64,{yekan_heavy}) format('woff2');
        font-weight: 800;
        font-style: normal;
    }}
    @font-face {{
        font-family: 'YekanBakhFaNum';
        src: url(data:font/woff2;base64,{yekan_light}) format('woff2');
        font-weight: 300;
        font-style: normal;
    }}
    @font-face {{
        font-family: 'YekanBakhFaNum';
        src: url(data:font/woff2;base64,{yekan_medium}) format('woff2');
        font-weight: 500;
        font-style: normal;
    }}
    @font-face {{
        font-family: 'YekanBakhFaNum';
        src: url(data:font/woff2;base64,{yekan_regular}) format('woff2');
        font-weight: normal;
        font-style: normal;
    }}


    </style>
    """, unsafe_allow_html=True)
    st.markdown(
        f"""
        <style>
        html, body, [class*="st-"] {{
            font-family: 'YekanBakhFaNum'!important;\
            font-size:22px !important;
            word-spacing: 1px;
        }}

        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('data:image/png;base64,{bg}') no-repeat center center;
            background-size: cover;
            filter: blur(2.5px);

        }}

        .stSidebar::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('data:image/png;base64,{bg}') no-repeat center center;
            background-size: cover;
            z-index: -1;       
            filter: blur(1.5px);

        }}
        [data-baseweb="modal"] [role="dialog"]{{
            background:white;
        }}
        .stExpander{{
        border-radius: 40px;
        background-color: #ffffffe0;
        }}  
        .stForm {{
        border-radius: 40px;
        background-color: #ffffffe0;
        }}
        .stExpander details{{
            border-radius: 40px;
        }}
        h1,h2,h3,h4,h5,h6,span
            {{
            font-family:'YekanBakhFaNum' !important;
            font-weight:300 !important;
        }}

        [kind="headerNoPadding"] {{
            background-color: white;
        }}
        [kind="headerNoPadding"]:hover {{
            background-color: white !important;
        }}
        .stMain {{
            direction: rtl !important;
        }}
        section[data-testid="stSidebar"] {{
            direction: rtl;
        }}
        [data-testid="stSidebar"]{{
            height: 100% !important;

        }}
        .stCheckbox {{
            display: flex;
            justify-content: center;
        }}
        [data-testid="stHeaderActionElements"] {{
            display:none;
        }}
        .stCheckbox {{
            direction: ltr !important;
        }}
        .stSidebar > .stCheckbox > label {{
            text-align: center !important;
        }}
        div.stButton>[disabled] {{
            color: #767b81 !important;
            background-color: #aec5dc !important;
        }}
        [kind="secondaryFormSubmit"][disabled] {{
            color: #767b81 !important;
            background-color: #aec5dc !important;                
        }}
        [kind="secondaryFormSubmit"] {{
            background-color: rgb(13, 110, 253) !important;
            color: white !important;
            border-radius: 100px !important;
            border: none !important;
            cursor: pointer !important;
            transition: 0.5s ease-in-out, transform 0.2s !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important;
            background-image: linear-gradient(180deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0)) !important;
        }}
        div.stButton > button ,[data-testid="stBaseButton-secondary"]{{
            background-color: rgb(13, 110, 253) !important;
            color: white !important;
            border-radius: 100px !important;
            border: none !important;
            cursor: pointer !important;
            transition: 0.5s ease-in-out, transform 0.2s !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important;
            background-image: linear-gradient(180deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0)) !important;
        }}
        div.stButton>[class*="st-"] {{
            padding:0 ;
        }}
        div.stButton > button p {{
            font-size: 19px !important;
            font-weight: 300 !important;
        }}
        div.stButton > button p ,[data-testid="stBaseButton-secondary"] p {{
            font-size: 19px !important;
            font-weight: 300 !important;
        }}
        [kind="secondaryFormSubmit"] p {{
            font-size: 19px !important;
            font-weight: 300 !important;
        }}
        .dataframe th {{
            font-size: 18px !important;
        }}
        .dataframe td {{
            font-size: 18px !important;
            text-align: center !important;
        }}
        .st-emotion-cache-1czn7q6 {{
            display: none !important;
        }}
        section[data-testid="stSidebar"] {{
            position: fixed !important;  /* ثابت روی صفحه */
            top: 0;
            left: 0;
            height: 100%;
            width: 300px; /* یا هر عرض مناسب */
            overflow-y: auto !important; /* اسکرول عمودی فعال */
            box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
            visibility: visible; 
        }}

        section[data-testid="stSidebar"] > div {{
            overflow-y: auto !important;
            max-height: 100vh !important;
        }}
        [data-testid="stSidebarCollapseButton"]{{
            display: inline-flex !important;
        }}
        @media (min-width: 1231px) {{
            section[data-testid="stSidebar"] {{
                min-width:400px;
                max-width:450px;
                visibility:visible;
            }}
            .stSidebar[aria-expanded="true"]{{
                position: relative !important;
            }}
        }}
        @media (min-width: 600px) {{
            .stApp::before {{
                filter: blur(3.5px);
            }}
        }}
        @media (min-width: 1200px) {{
            .stApp::before {{
                filter: blur(5.5px);
            }}
        }}

        [data-testid="stCheckbox"] [data-testid="stWidgetLabel"] p {{
            font-size: 20px !important;
        }}
        @media (max-width:460px){{
            [role="dialog"]{{
                min-width:100px
            }}
        }}
        

            
        div.stButton > button:hover ,[data-testid="stBaseButton-secondary"]:hover{{
            background: rgb(17, 72, 151) !important;
            transform: scale(1.05) !important;
        }}
        .stSidebar[aria-expanded="true"] {{
            visibility:visible;
        }}
        [kind="secondaryFormSubmit"]:hover {{
            background: rgb(17, 72, 151) !important;
            transform: scale(1.05) !important;
        }}
        [data-baseweb="input"] {{
            font-family: 'YekanBakhFaNum'!important;
            height: max-content !important;
            direction: ltr !important;
        }}
        .stTextInput > [data-testid="stWidgetLabel"] p {{
            font-size: 17px !important;
        }}
        input {{
            font-size: 23px !important;
        }}
        div.stButton > button:active ,[data-testid="stBaseButton-secondary"]:active {{
            background: rgb(38, 63, 100) !important;
            transform: scale(0.95) !important;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2) !important;
            color: white !important;
        }}
        [kind="secondaryFormSubmit"]:active {{
            background: rgb(38, 63, 100) !important;
            transform: scale(0.95) !important;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2) !important;
            color: white !important;
        }}
        .st-key-title_sets{{
            padding:20px;
            border-radius: 40px;
            background-color: #ffffffcc;
        }}
        .st-key-title_menu h1{{
            background: #ffffffcc;
            padding: 9px;
            margin-bottom: 22px;
            border-radius: 72px;
        }}
        .st-key-title_menu{{
            display: flex;
            align-items: center;
        }}
        hr {{
            background: black !important;
            height: 2px !important;
            border-radius: 100% !important;
        }}
        .stSelectbox{{
            padding:20px !important; 
            border-radius: 40px !important;
            background-color: #ffffffcc !important;
        }}
        [data-baseweb="select"]{{
            border: 1px solid;
            border-radius: 13px;
        }}
        .st-key-display_set{{
            padding: 10px !important;
            padding-top:30px !important; 
            border-radius: 40px !important;
            background-color: #ffffffe0 !important;
        }}
        .st-key-setting_of_ai{{
            padding: 20px !important;
            border-radius: 40px !important;
            direction: ltr;
            text-align: center;
            background-color: #ffffffcc !important;

            gap: 40px;
        }}
        .st-key-setting_of_ai p{{
            font-size: 16px !important;
        }}
        .st-key-setting_of_ai label {{
            direction: rtl !important;
        }}

        .st-key-setting_of_ai [data-testid="stSliderTickBarMax"]{{
            font-size: 16px !important;
            font-weight: bolder;
        }}
        .st-key-setting_of_ai [data-testid="stSliderThumbValue"]{{
            font-size: 16px !important;
            font-weight: bolder;
        }}
        .st-key-setting_of_ai [data-testid="stSliderTickBarMin"]{{
            font-size: 16px !important;
            font-weight: bolder;
        }}

        [data-baseweb="popover"] {{
            background: white;
        }}
        @media (max-width:460px){{
            .st-key-setting_of_ai [data-testid="stSliderTickBarMax"]{{
                font-size: 12px !important;
                font-weight: bolder;
            }}
            .st-key-setting_of_ai [data-testid="stSliderThumbValue"]{{
                font-size: 12px !important;
                font-weight: bolder;
            }}
            .st-key-setting_of_ai [data-testid="stSliderTickBarMin"]{{
                font-size: 12px !important;
                font-weight: bolder;
            }}

        }}
        .st-key-chat_frame {{
            padding: 10px !important;
            border-radius: 40px !important;
            background-color: #ffffffe0 !important;
        }}

        .stChatMessage:has([aria-label="Chat message from 🫵"]){{
            background: #008aa63d;
            padding: 15px;
            border-radius: 35px;
        }}
        .stChatMessage:has([aria-label="Chat message from 🤖"]){{
            background: #b9000029;
            padding: 15px;
            border-radius: 35px;
        }}
        .st-key-input_frame {{
            position: fixed;
            bottom: 18px;
        }}
        [data-testid="stFileUploaderDropzone"] button{{
            width:100%;
            font-size:18px !important;

        }}
        [data-testid="stFileUploaderDropzone"] small{{
            font-size:18px !important;
        }}
        [data-testid="stFileUploaderDropzone"] span{{
            font-size:18px !important;
        }}
        span.katex-html {{
            direction: ltr;
        }}
        .katex-display {{
            display: block;
            position: relative;
            word-wrap: break-word;
            overflow-x: auto;
            max-width: 100%;
            text-align: center;
            white-space: normal;  /* متن را مجاز به شکستن کند */
        }}

        .katex {{
            display: inline-block !important; /* اطمینان از اینکه KaTeX قابل شکستن باشد */
            word-break: break-word;  /* اجازه شکستن کلمات */
            overflow-wrap: break-word; /* کمک به شکستن کلمات */
        }}
        </style>
        """, unsafe_allow_html=True
    )

# ====================================
# سایر توابع و کلاس‌های برنامه (مانند initialize_session_state، safe_rerun، کلاس LineAlgorithm و صفحات)
def initialize_session_state():
    defaults = {
        "registered_lines": [],
        "delete_index": None,
        "eq_system": [""],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def safe_rerun():
    try:
        st.experimental_rerun()
    except Exception:
        pass

class LineAlgorithm:
    def __init__(self):
        self.x, self.y = sp.symbols('x y')
    
    def parse_equation(self, equation):
        original_eq = equation.strip()
        eq_processed = original_eq.replace('^', '**')  # Replace ^ with ** for exponentiation
        transformations = standard_transformations + (implicit_multiplication_application,)
        try:
            if "=" in eq_processed:
                left_str, right_str = eq_processed.split("=")
                left_expr = parse_expr(left_str, transformations=transformations, local_dict={'x': self.x, 'y': self.y})
                right_expr = parse_expr(right_str, transformations=transformations, local_dict={'x': self.x, 'y': self.y})
                expr = sp.simplify(left_expr - right_expr)  # Move everything to one side (e.g., y^2 - 7x^2 - 6y = 0)
            else:
                expr = parse_expr(eq_processed, transformations=transformations, local_dict={'x': self.x, 'y': self.y})

            # Try solving for y
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
                elif deg is not None and deg > 1:
                    info = f"معادله چندجمله‌ای: y = {sp.pretty(sol)}"
                    return ("parabolic", sol, None, None, info)
                else:
                    info = f"معادله منحنی: y = {sp.pretty(sol)}"
                    return ("curve", sol, None, None, info)
            else:
                # Try solving for x
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
                    # If neither x nor y can be isolated, treat as implicit
                    info = f"معادله ضمنی: {sp.pretty(expr)} = 0"
                    return ("implicit", expr, None, None, info)
        except Exception as e:
            st.error("خطا در تبدیل معادله: " + str(e))
            return ("error", None, None, None, "خطا در تبدیل معادله.")

    def plot_equation(self, equation):
        result = self.parse_equation(equation)
        eq_type, sol, m, b, info = result
        plt.figure(figsize=(6, 4))
        
        if eq_type == "error":
            return info
        
        x_vals = np.linspace(-10, 10, 400)
        if eq_type == "linear":
            func = sp.lambdify(self.x, sol, 'numpy')
            y_vals = func(x_vals)
            plt.plot(x_vals, y_vals, label=f'y = {sp.pretty(sol)}')
        
        elif eq_type == "implicit_multiple":
            for idx, s in enumerate(sol):
                try:
                    func = sp.lambdify(self.x, s, 'numpy')
                    y_vals = func(x_vals)
                    plt.plot(x_vals, y_vals, label=f'Branch {idx+1}: y = {sp.pretty(s)}')
                except Exception as e:
                    st.error(f"خطا در رسم شاخه {idx+1}: {str(e)}")
        
        elif eq_type in ["curve", "parabolic", "implicit_x"]:
            try:
                func = sp.lambdify(self.x, sol, 'numpy')
                y_vals = func(x_vals)
                plt.plot(x_vals, y_vals, label=f'{equation}')
            except Exception as e:
                st.error(f"خطا در تبدیل به تابع: {str(e)}")
        
        elif eq_type == "implicit":
            # Implicit plotting using contour
            X, Y = np.meshgrid(np.linspace(-10, 10, 200), np.linspace(-10, 10, 200))
            try:
                func = sp.lambdify((self.x, self.y), sol, 'numpy')
                Z = func(X, Y)
                plt.contour(X, Y, Z, levels=[0], colors='b')
                plt.title(f'{equation} = 0')
            except Exception as e:
                st.error(f"خطا در رسم معادله ضمنی: {str(e)}")
                return info
        
        ax = plt.gca()
        ax.xaxis.set_major_locator(plt.MultipleLocator(5))
        ax.yaxis.set_major_locator(plt.MultipleLocator(5))
        plt.grid(True, linestyle='--', linewidth=0.5)
        plt.xlabel('x')
        plt.ylabel('y')
        if eq_type != "implicit":
            plt.legend(fontsize='small')
        plt.title('نمودار معادله')
        plt.tight_layout()
        return info

    def calculate_from_points(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        if x1 == x2:
            raise ValueError("مقادیر x نقاط نباید برابر باشند.")
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1
        return m, b
    
    def plot_line_from_points(self, m, b):
        distance = abs(b) / sp.sqrt(m**2 + 1)
        distance = float(distance)
        x_vals = np.linspace(-20, 20, 400)
        y_vals = m * x_vals + b
        plt.figure(figsize=(6, 4))
        plt.plot(x_vals, y_vals, label=f'y = {m:.2f}x + {b:.2f}')
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.grid(True, linestyle='--', linewidth=0.5)
        plt.xlabel('x')
        plt.ylabel('y')
        plt.xticks(np.arange(-20, 21, 2))
        plt.yticks(np.arange(-20, 21, 2))
        plt.legend()
        plt.title('نمودار خط')
        plt.tight_layout()
        info = f"شیب = {m:.2f}، عرض = {b:.2f}، فاصله = {distance:.2f}"
        return info

# Update the linear_equations_page to use the modified plotting
def linear_equations_page():

    if "registered_lines" not in st.session_state:
        st.session_state.registered_lines = []
    if "delete_index" not in st.session_state:
        st.session_state.delete_index = None
    line_name = st.text_input("نام خط:", key="line_name_main")
    input_type = st.radio("نوع ورود خط:", ("معادله", "نقطه‌ای"))
    if input_type == "معادله":
        eq_input = st.text_input("معادله خطی وارد کنید :", key="eq_input_main")
    else:
        st.markdown("### نقطه اول")
        col1, col2 = st.columns(2)
        pt1_x = col1.text_input("مقدار x نقطه اول:", key="pt1_x")
        pt1_y = col2.text_input("مقدار y نقطه اول:", key="pt1_y")
        st.markdown("### نقطه دوم")
        col3, col4 = st.columns(2)
        pt2_x = col3.text_input("مقدار x نقطه دوم:", key="pt2_x")
        pt2_y = col4.text_input("مقدار y نقطه دوم:", key="pt2_y")
    calculator = LineAlgorithm()
    with st.form("input_form", clear_on_submit=True):
        submitted = st.form_submit_button("ثبت اطلاعات")
    if submitted:
        if len(line_name) != 1 or line_name not in string.ascii_letters:
            st.error("نام خط باید تنها یک حرف انگلیسی باشد (مثلاً A).")
        else:
            if not line_name.isupper():
                st.warning("نام خط به حروف بزرگ تبدیل شد.")
                line_name = line_name.upper()
            duplicate = any(line["name"] == line_name for line in st.session_state.registered_lines)
            if duplicate:
                st.error("نام خط تکراری است.")
            else:
                if input_type == "معادله":
                    if not eq_input:
                        st.error("لطفاً معادله را وارد کنید.")
                    else:
                        result = calculator.parse_equation(eq_input)
                        eq_type = result[0]
                        if eq_type == "error":
                            st.error("فرمت معادله صحیح نیست.")
                        else:
                            st.success("خط با موفقیت ثبت شد.")
                            if eq_type == "general":
                                _, expr, a, b_coef, c, info = result
                                st.session_state.registered_lines.append({
                                    "name": line_name,
                                    "type": "general",
                                    "a": float(a),
                                    "b_coef": float(b_coef),
                                    "c": float(c),
                                    "input": eq_input,
                                    "info": info
                                })
                            elif eq_type == "quadratic":
                                _, sol, a, b_coef, c, delta, info = result
                                st.session_state.registered_lines.append({
                                    "name": line_name,
                                    "type": "quadratic",
                                    "a": float(a),
                                    "b_coef": float(b_coef),
                                    "c": float(c),
                                    "delta": float(delta),
                                    "input": eq_input,
                                    "info": info
                                })
                            else:
                                _, sol, m, b, info = result
                                st.session_state.registered_lines.append({
                                    "name": line_name,
                                    "type": eq_type,
                                    "m": float(m) if m is not None else None,
                                    "b": float(b) if b is not None else None,
                                    "input": eq_input,
                                    "info": info
                                })
                            safe_rerun()
                else:
                    if not pt1_x or not pt1_y or not pt2_x or not pt2_y:
                        st.error("لطفاً مقدارهای x و y هر دو نقطه را وارد کنید.")
                    else:
                        try:
                            point1 = (float(pt1_x), float(pt1_y))
                            point2 = (float(pt2_x), float(pt2_y))
                        except Exception:
                            st.error("فرمت مقادیر عددی صحیح نیست.")
                        else:
                            try:
                                m_val, b_val = calculator.calculate_from_points(point1, point2)
                            except Exception as e:
                                st.error(str(e))
                            else:
                                distance = abs(b_val) / np.sqrt(m_val**2+1)
                                computed_form = f"y = {m_val:.2f}x + {b_val:.2f}"
                                info = f"شیب = {m_val:.2f}، عرض = {b_val:.2f}، فاصله = {distance:.2f}"
                                st.success("خط با موفقیت ثبت شد.")
                                st.session_state.registered_lines.append({
                                    "name": line_name,
                                    "type": "linear",
                                    "m": float(m_val),
                                    "b": float(b_val),
                                    "input": computed_form,
                                    "info": info
                                })
                                safe_rerun()
    if st.button("رسم خطوط"):
        if not st.session_state.registered_lines:
            st.error("هیچ خطی ثبت نشده است.")
        else:
            # تعریف صریح شکل و محور
            fig, ax = plt.subplots(figsize=(8, 6))
            x_vals = np.linspace(-20, 20, 400)
            ax.xaxis.set_major_locator(MultipleLocator(15))
            ax.yaxis.set_major_locator(MultipleLocator(15))
            ax.grid(which='major', linestyle='-', linewidth=0.75)
            ax.grid(which='minor', linestyle=':', linewidth=0.5)
            intersections = []
            letter_index = 0
            
            for line in st.session_state.registered_lines:
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
                        func = sp.lambdify(calculator.x, a * calculator.x**2 + b_coef * calculator.x + c, 'numpy')
                        y_vals = func(x_vals)
                        ax.plot(x_vals, y_vals, label=f"{line['name']}: {a}x² + {b_coef}x + {c}")
                else:
                    m_line = line.get("m", None)
                    b_line = line.get("b", None)
                    if m_line is None or b_line is None:
                        expr_str = line["input"]
                        if expr_str.lower().startswith("y="):
                            expr_str = expr_str[2:]
                        try:
                            func = sp.lambdify(calculator.x, sp.sympify(expr_str, locals={'x': calculator.x, 'y': calculator.y}), 'numpy')
                            y_vals = func(x_vals)
                            ax.plot(x_vals, y_vals, label=f"{line['name']}: {line['input']}")
                        except Exception as e:
                            st.error("Error in curve plotting: " + str(e))
                    else:
                        y_vals = m_line * x_vals + b_line
                        ax.plot(x_vals, y_vals, label=f"{line['name']}: y = {m_line:.2f}x + {b_line:.2f}")
            
            # محاسبه تقاطع‌ها
            n = len(st.session_state.registered_lines)
            for i in range(n):
                for j in range(i + 1, n):
                    line_i = st.session_state.registered_lines[i]
                    line_j = st.session_state.registered_lines[j]
                    if line_i.get("type", "linear") == "linear" and line_j.get("type", "linear") == "linear":
                        m1 = line_i["m"]
                        b1 = line_i["b"]
                        m2 = line_j["m"]
                        b2 = line_j["b"]
                        if m1 is not None and m2 is not None and abs(m1 - m2) > 1e-9:
                            x_int = (b2 - b1) / (m1 - m2)
                            y_int = m1 * x_int + b1
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
            
            # اضافه کردن خطوط محورها
            ax.axhline(0, color='black', linewidth=0.5)
            ax.axvline(0, color='black', linewidth=0.5)
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.legend(fontsize='small', loc='best')
            st.pyplot(fig)
    
    # بقیه کد (نمایش اطلاعات خطوط و حذف) بدون تغییر باقی می‌ماند
    st.markdown("---")
    st.subheader("اطلاعات خطوط ثبت‌شده")
    def delete_line(idx):
        st.session_state.registered_lines.pop(idx)
        safe_rerun()
    if st.session_state.registered_lines:
        header_cols = st.columns([1, 1, 2, 1, 1, 1, 1, 1, 1, 1])
        header_cols[0].write(".")
        header_cols[1].write("نام خط")
        header_cols[2].write("معادله")
        header_cols[3].write("شیب خط")
        header_cols[4].write("عرض از مبدا")
        header_cols[5].write("طول از مبدا")
        header_cols[6].write("a")
        header_cols[7].write("b")
        header_cols[8].write("c")
        header_cols[9].write("△/دلتا")
        for idx, line in enumerate(st.session_state.registered_lines):
            cols = st.columns([1, 1, 2, 1, 1, 1, 1, 1, 1, 1])
            if cols[0].button("🗑", key=f"delete_{idx}"):
                with st.expander("تأیید حذف", expanded=True):
                    st.info(f"آیا مطمئن هستید که می‌خواهید خط {line['name']} را حذف کنید؟")
                    col_yes, col_no = st.columns(2)
                    col_yes.button("بله", key=f"confirm_yes_{idx}", use_container_width=True, on_click=delete_line, args=(idx,))
                    col_no.button("خیر", key=f"confirm_no_{idx}", use_container_width=True)
            cols[1].write(line["name"])
            cols[2].write(line["input"])
            if line.get("type", "linear") in ["general", "quadratic"]:
                if line["type"] == "general":
                    cols[3].write("-")
                    cols[4].write("-")
                    cols[5].write("-")
                    cols[6].write(line["a"])
                    cols[7].write(line["b_coef"])
                    cols[8].write(line["c"])
                    delta = abs(line["c"]) / np.sqrt(line["a"]**2 + line["b_coef"]**2) if (line["a"]**2 + line["b_coef"]**2) != 0 else "-"
                    cols[9].write(f"{delta:.2f}" if delta != "-" else "-")
                else:
                    cols[3].write("-")
                    cols[4].write("-")
                    cols[5].write("-")
                    cols[6].write(line["a"])
                    cols[7].write(line["b_coef"])
                    cols[8].write(line["c"])
                    cols[9].write(f"{line['delta']:.2f}")
            else:
                cols[3].write(f"{line['m']:.2f}" if line.get("m") is not None else "-")
                cols[4].write(f"{line['b']:.2f}" if line.get("b") is not None else "-")
                if line.get("m") is not None and line.get("b") is not None:
                    distance = abs(line['b']) / np.sqrt(line['m']**2 + 1)
                    cols[5].write(f"{distance:.2f}")
                else:
                    cols[5].write("-")
                cols[6].write("-")
                cols[7].write("-")
                cols[8].write("-")
                cols[9].write("-")
    else:
        st.write("هیچ خطی ثبت نشده است.")

def equations_solver_page():
    st.title("حل معادلات")
    st.markdown("در این صفحه می‌توانید معادلات تک‌متغیره یا چندمتغیره را وارد و حل کنید.")
    system_mode = st.checkbox("حالت دستگاه (چند معادله)", value=False)
    if not system_mode:
        eq_input = st.text_input("معادله را وارد کنید:")
        if st.button("حل معادله"):
            try:
                transformations = standard_transformations + (implicit_multiplication_application,)
                if "=" in eq_input:
                    left_str, right_str = eq_input.split("=")
                    left_expr = parse_expr(left_str, transformations=transformations)
                    right_expr = parse_expr(right_str, transformations=transformations)
                    eq_expr = sp.Eq(left_expr, right_expr)
                else:
                    expr = parse_expr(eq_input, transformations=transformations)
                    eq_expr = sp.Eq(expr, 0)
                vars_in_eq = list(eq_expr.free_symbols)
                solution = sp.solve(eq_expr, vars_in_eq, dict=True)
                st.write("متغیرهای موجود:", vars_in_eq)
                st.write("جواب معادله:")
                st.write(solution)
            except Exception as e:
                st.error("خطا در حل معادله: " + str(e))
    else:
        st.subheader("ورود معادلات دستگاه")
        if "eq_system" not in st.session_state:
            st.session_state.eq_system = [""]
        for i, eq in enumerate(st.session_state.eq_system):
            eq_input = st.text_input(f"معادله {i+1}:", value=eq, key=f"sys_eq_{i}")
            st.session_state.eq_system[i] = eq_input
            if i == len(st.session_state.eq_system) - 1:
                if st.button("➕ اضافه معادله", key=f"add_eq_button_{i}"):
                    st.session_state.eq_system.append("")
                    safe_rerun()
        if st.button("حل دستگاه", key="solve_system_button"):
            try:
                eq_list = []
                transformations = standard_transformations + (implicit_multiplication_application,)
                for eq_str in st.session_state.eq_system:
                    if eq_str:
                        if "=" in eq_str:
                            left_str, right_str = eq_str.split("=")
                            left_expr = parse_expr(left_str, transformations=transformations)
                            right_expr = parse_expr(right_str, transformations=transformations)
                            eq_list.append(sp.Eq(left_expr, right_expr))
                        else:
                            expr = parse_expr(eq_str, transformations=transformations)
                            eq_list.append(sp.Eq(expr, 0))
                vars_all = set()
                for eq in eq_list:
                    vars_all = vars_all.union(eq.free_symbols)
                vars_all = list(vars_all)
                solution = sp.solve(eq_list, vars_all, dict=True)
                eq_data = {"شماره": [i+1 for i in range(len(eq_list))], "معادله": st.session_state.eq_system}
                df = pd.DataFrame(eq_data)
                st.table(df)
                st.write("جواب دستگاه:")
                st.write(solution)
            except Exception as e:
                st.error("خطا در حل دستگاه: " + str(e))

def main():
    setup_page()  # فراخوانی استایل‌ها در ابتدای برنامه
    initialize_session_state()
    st.sidebar.title("انتخاب صفحه")
    page = st.sidebar.radio("صفحه مورد نظر را انتخاب کنید:", options=["معادلات خطی", "حل معادلات"])
    if page == "معادلات خطی":
        linear_equations_page()
    else:
        equations_solver_page()

if __name__ == '__main__':
    main()

