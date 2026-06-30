import streamlit as st

from utils.database import init_db, login_user, register_user
from pages import admin, company, customer

st.set_page_config(page_title="ComplaintSense", page_icon="🧠", layout="wide")

init_db()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None

def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

def show_auth():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align:center'>🧠 ComplaintSense</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:gray'>Tanzania Complaint Intelligence Platform</p>", unsafe_allow_html=True)
        st.divider()

        tab_login, tab_register = st.tabs(["Login", "Register"])

        with tab_login:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("Login", use_container_width=True):
                if not email or not password:
                    st.error("Please fill in all fields")
                else:
                    success, user = login_user(email, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("Invalid email or password")

            st.info("**Default Admin Login:**\n\nEmail: admin@complaintsense.com\n\nPassword: admin123")

        with tab_register:
            name = st.text_input("Full Name", key="reg_name")
            email_r = st.text_input("Email", key="reg_email")
            password_r = st.text_input("Password", type="password", key="reg_password")
            role = st.selectbox("Account Type", ["customer", "company", "admin"])

            if st.button("Create Account", use_container_width=True):
                if not name or not email_r or not password_r:
                    st.error("Please fill in all fields")
                else:
                    success, msg = register_user(name, email_r, password_r, role)
                    if success:
                        st.success(msg + " — Please login.")
                    else:
                        st.error(msg)

def show_app():
    user = st.session_state.user

    with st.sidebar:
        st.markdown("### 🧠 ComplaintSense")
        st.markdown(f"👤 **{user.name}**")
        st.markdown(f"🏷️ Role: `{user.role}`")
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout()

    if user.role == 'admin':
        admin.show()
    elif user.role == 'company':
        company.show(user)
    else:
        customer.show(user)

if not st.session_state.logged_in:
    show_auth()
else:
    show_app()
