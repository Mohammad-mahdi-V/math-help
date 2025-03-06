import streamlit as st
import base64

class app:
    def __init__(self):
        # خواندن و تبدیل فونت به Base64
        with open("data/font/FarhangVariable.woff", "rb") as font_file:
            encoded_font = base64.b64encode(font_file.read()).decode('utf-8')

        # اعمال CSS برای فونت
        st.markdown(
            f"""
            <style>
            @font-face {{
            font-family: 'Farhang';
            src: url(data:font/woff;base64,{encoded_font}) format('woff');
            font-display: fallback;
            }}
            .st-emotion-cache-3gzemd h1, .st-emotion-cache-3gzemd h2, .st-emotion-cache-3gzemd h3, .st-emotion-cache-3gzemd h4, .st-emotion-cache-3gzemd h5, .st-emotion-cache-3gzemd h6 {{
            font-family: 'Farhang' !important;
            font-weight: none;
            line-height: 1.2;
            margin: 0px;
            color: inherit;
            text-align: none;
            }}
            html, body, [class*="st-"] {{            
            font-family: 'Farhang' !important;
            }}
            .stMain{{
                direction: rtl !important;
            }}
            section[data-testid="stSidebar"] {{
            direction: rtl;  /* متن داخل سایدبار راست‌چین شود */
            }}
            .stSidebar .stCheckbox{{
                display: flex;
                justify-content: center;
            }}
            .stSidebar{{
                min-width:400px;
                max-width:450px;
            }}
            .stCheckbox{{
                direction: ltr !important;
            }}
            .stSidebar>.stCheckbox>label{{
                text-algin:center !important;
            }}

            div.stButton > button {{
                background-color:  rgb(13, 110, 253)!important;
                color: white !important;
                font-size: 20px !important;
                border-radius: 100px !important;
                border: none !important;
                cursor: pointer !important;
                transition:  0.5s ease-in-out, transform 0.2s !important;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important;
                background-image: linear-gradient(180deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0)) !important
            }}
            .st-emotion-cache-1wqrzgl{{
                min-width: 400px !important; /* عرض سایدبار */
            }}
            /* استایل دکمه هنگام هاور */
            div.stButton > button:hover {{
                background: rgb(17 72 151) !important;
                transform: scale(1.05) !important;
            }}

            div.stButton > button:focus {{
                background: rgb(157 203 249) !important;
                color: black !important;
                transform: scale(1.05) !important;
            }}

            /* استایل دکمه هنگام کلیک */
            div.stButton > button:active {{
                background: rgb(38 63 100) !important;
                transform: scale(0.95) !important;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2) !important;
                color: white !important;
            }}
            </style>"""
            ,unsafe_allow_html=True)
        
        if "show_sets" not in st.session_state:
            st.session_state["show_sets"]=False 
        if "show_hr_sidebar" not in st.session_state:
            st.session_state["show_hr_sidebar"] = False
        self.main_menu()
    def main_menu(self):
        # اصلاح `st.sidebar.title` (نباید داخل `with` باشه)
        st.sidebar.markdown("<h1  style='color: #ff0000; font-weight:600;text-align:center;'>منو اصلی</h1>", unsafe_allow_html=True)
        with st.sidebar.container():
            # قرار دادن دکمه‌ها در کنار هم با استفاده از st.columns
            col1, col2 = st.sidebar.columns([1, 1])  # تنظیم دو ستون در سایدبار
            with col1:
                if st.button("مجموعه ها", key="sets_button",use_container_width=True):
                        st.session_state["show_hr_sidebar"]=True
                        st.session_state["show_sets"]=True
                        st.session_state["active_section"] = "sets"

            with col2:
                if st.button("خط", key="lines_button",use_container_width=True):
                    self.show_lines_section()
                    st.session_state["active_section"] = "lines"


        # دکمه سوم در سایدبار
        if st.sidebar.button("گفتگو با هوش مصنوعی",use_container_width=True):
            st.session_state["active_section"] = "chatbot"
            self.show_chatbot_section()
        if st.session_state["show_hr_sidebar"]:
            st.sidebar.markdown("<hr>", unsafe_allow_html=True)
        if st.session_state['show_sets']:
            advane_toggel=st.sidebar.toggle("حالت پیشرفته",value=False)
            if st.sidebar.button("ثبت اطلاعات",key="add_set",use_container_width=True):
                self.next_set()
            if st.sidebar.button("مجموعه قبلی",use_container_width=True):
                self.privous_set()
            if st.sidebar.button("پردازش مجموعه ها",use_container_width=True):
                self.display_sets()
        st.sidebar.markdown("<hr>",unsafe_allow_html=True)
        with st.sidebar.container():
            col1,col2=st.sidebar.columns([1, 1]) 
            with col1:
                if st.button("درباره ما", key="about-us",use_container_width=True):
                    self.about_us()
                    st.session_state["active_section"] = "about"

            with col2:
                if st.button("نحوه کار در این بخش", key="how-to-us",use_container_width=True):
                    self.how_to_us()
                    st.session_state["active_section"] = "howto"

        if st.session_state["show_sets"]:
            self.sets_section()
    def active_page(self):
        active = st.session_state["active_section"]
        active_css = ""
        if active == "sets":
            active_css = """
            <style>
            /* فرض می‌کنیم دکمه "مجموعه ها" اولین دکمه در container اول سایدبار است */
            div[data-testid="stHorizontalBlock"] div:nth-child(1) button {
                background: rgb(157,203,249)!important;
                color: black !important;
                transform: scale(1.05)!important;
            }
            </style>
            """
        elif active == "lines":
            active_css = """
            <style>
            /* فرض می‌کنیم دکمه "خط" دومین دکمه در container اول سایدبار است */
            div[data-testid="stHorizontalBlock"] div:nth-child(2) button {
                background: rgb(157,203,249)!important;
                color: black !important;
                transform: scale(1.05)!important;
            }
            </style>
            """
        elif active == "chatbot":
            active_css = """
            <style>
            /* استایل برای دکمه گفتگو با هوش مصنوعی (با استفاده از aria-label یا سایر ویژگی‌ها) */
            button[aria-label="گفتگو با هوش مصنوعی"] {
                background: rgb(157,203,249)!important;
                color: black !important;
                transform: scale(1.05)!important;
            }
            </style>
            """
        elif active == "about":
            active_css = """
            <style>
            /* فرض می‌کنیم دکمه "درباره ما" اولین دکمه در container دوم سایدبار است */
            div[data-testid="stHorizontalBlock"] div:nth-child(1) button {
                background: rgb(157,203,249)!important;
                color: black !important;
                transform: scale(1.05)!important;
            }
            </style>
            """
        elif active == "howto":
            active_css = """
            <style>
            /* فرض می‌کنیم دکمه "نحوه کار در این بخش" دومین دکمه در container دوم سایدبار است */
            div[data-testid="stHorizontalBlock"] div:nth-child(2) button {
                background: rgb(157,203,249)!important;
                color: black !important;
                transform: scale(1.05)!important;
            }
            </style>
            """
        st.markdown(active_css, unsafe_allow_html=True)

    def sets_section(self):
        if "num_sets" not in st.session_state:
            st.session_state["num_sets"]=1
        with st.container():
            name_sets = st.text_input(f"نام مجموعه {st.session_state.num_sets} را وارد کنید:")


    def show_lines_section(self):
        pass
    def next_set(self):
        pass
    def privous_set(self):
        pass
    def display_sets():
        pass
    def show_chatbot_section(self):
        pass
    def about_us(self):
        pass
    def how_to_us(self):
        pass

# اجرای اپلیکیشن
app()
