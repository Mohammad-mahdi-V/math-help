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
            html, body, [class*="st-"] {{
            text-align: right !important;
            font-family: 'Farhang' !important;
            }}
            section[data-testid="stSidebar"] {{
            direction: rtl;
            }}
            </style>""",
            unsafe_allow_html=True
        )

        # مقداردهی اولیه متغیرها در session_state
        if "show_sets" not in st.session_state:
            st.session_state["show_sets"] = False 
        if "advane_toggel" not in st.session_state:
            st.session_state["advane_toggel"] = False  
        if "show_hr_sidebar" not in st.session_state:
            st.session_state["show_hr_sidebar"] = False  # 🔴 این خط را اضافه کردیم

        self.main_menu()

    def main_menu(self):
        st.sidebar.markdown("<h1 style='color: #ff0000; font-weight:600;text-align:center;'>منو اصلی</h1>", unsafe_allow_html=True)

        with st.sidebar.container():
            col1, col2 = st.sidebar.columns([1, 1])  

            with col1:
                if st.button("مجموعه ها", key="sets_button", use_container_width=True):
                    st.session_state["show_sets"] = not st.session_state["show_sets"]

            with col2:
                if st.button("خط", key="lines_button", use_container_width=True):
                    self.show_lines_section()

        if st.sidebar.button("گفتگو با هوش مصنوعی", use_container_width=True):
            self.show_chatbot_section()

        # 🔵 این قسمت را اصلاح کردیم
        if st.session_state["show_hr_sidebar"]:
            st.sidebar.markdown("<hr>", unsafe_allow_html=True)

        if st.session_state["show_sets"]:
            st.session_state["advane_toggel"] = st.sidebar.toggle("🔧 حالت پیشرفته", value=st.session_state["advane_toggel"])

            if st.session_state["advane_toggel"]:
                st.sidebar.success("✅ حالت پیشرفته فعال شد!")
            else:
                st.sidebar.warning("⚠️ حالت پیشرفته غیرفعال است!")

        st.sidebar.markdown("<hr>", unsafe_allow_html=True)

        with st.sidebar.container():
            col1, col2 = st.sidebar.columns([1, 1]) 
            with col1:
                if st.button("درباره ما", key="about-us", use_container_width=True):
                    self.about_us()
            with col2:
                if st.button("نحوه کار در این بخش", key="how-to-us", use_container_width=True):
                    self.how_to_us()

    def show_sets_section(self):
        pass

    def show_lines_section(self):
        pass

    def show_chatbot_section(self):
        pass

    def about_us(self):
        pass

    def how_to_us(self):
        pass

# اجرای اپلیکیشن
app()
