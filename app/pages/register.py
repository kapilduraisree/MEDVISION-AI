"""
MedVision AI – Register Page
"""
import re
import streamlit as st
from app.core.auth import register_user, is_authenticated


def _valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


def _valid_phone(phone: str) -> bool:
    digits = re.sub(r"\D", "", phone)
    return 7 <= len(digits) <= 15


def show():
    if is_authenticated():
        st.session_state["active_page"] = "dashboard"
        st.rerun()

    st.markdown("""
    <div style="text-align:center; padding: 1.5rem 0 0.8rem 0;">
        <h1 style="font-size:2.2rem; color:#0EA5E9; margin-bottom:0;">🏥 MedVision AI</h1>
        <p style="color:#94A3B8; margin-top:6px;">Create your account</p>
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "⚠️ For educational use only. AI-generated content must be reviewed by a healthcare professional.",
        icon="ℹ️",
    )
    st.markdown("---")

    col_l, col_form, col_r = st.columns([1, 1.6, 1])
    with col_form:
        st.markdown("### New Account")

        with st.form("register_form", clear_on_submit=False):
            full_name = st.text_input("Full Name *", placeholder="Dr. Priya Sharma")
            email = st.text_input("Email Address *", placeholder="you@example.com")
            phone = st.text_input("Phone Number *", placeholder="+91 98765 43210")

            role = st.selectbox(
                "Account Type *",
                options=["patient", "doctor"],
                format_func=lambda r: "🧑‍⚕️ Patient" if r == "patient" else "👨‍⚕️ Doctor",
            )

            st.markdown("**Password**")
            password = st.text_input("Password *", type="password", placeholder="Min. 8 characters")
            confirm = st.text_input("Confirm Password *", type="password", placeholder="Repeat password")

            st.markdown(
                "<small style='color:#64748B;'>By creating an account you agree that this system "
                "is for informational / educational purposes only.</small>",
                unsafe_allow_html=True,
            )

            submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

        if submitted:
            errors = []
            if not full_name.strip():
                errors.append("Full name is required.")
            if not _valid_email(email):
                errors.append("Enter a valid email address.")
            if not _valid_phone(phone):
                errors.append("Enter a valid phone number.")
            if len(password) < 8:
                errors.append("Password must be at least 8 characters.")
            if password != confirm:
                errors.append("Passwords do not match.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                with st.spinner("Creating account…"):
                    ok, msg = register_user(email, full_name, phone, password, role)
                if ok:
                    st.success(msg)
                    st.balloons()
                    import time
                    time.sleep(1.5)
                    st.session_state["active_page"] = "login"
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center; color:#64748B;'>Already have an account?</div>",
            unsafe_allow_html=True,
        )
        if st.button("Sign In Instead", use_container_width=True):
            st.session_state["active_page"] = "login"
            st.rerun()
