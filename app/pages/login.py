"""
MedVision AI – Login Page
"""
import streamlit as st
from app.core.auth import login, is_authenticated
from app.core.config import settings


def show():
    if is_authenticated():
        st.session_state["active_page"] = "dashboard"
        st.rerun()

    # Hero banner
    st.markdown("""
    <div style="text-align:center; padding: 2rem 0 1rem 0;">
        <h1 style="font-size:2.6rem; color:#0EA5E9; margin-bottom:0;">🏥 MedVision AI</h1>
        <p style="color:#94A3B8; font-size:1.05rem; margin-top:6px;">
            Multimodal AI-Based Medicine &amp; Health Report Analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Disclaimer
    st.info(
        "⚠️ This system is for **educational and informational use only**. "
        "All AI-generated content must be reviewed by a qualified healthcare professional.",
        icon="ℹ️",
    )

    st.markdown("---")

    col_left, col_form, col_right = st.columns([1, 1.4, 1])
    with col_form:
        st.markdown("### Sign In")

        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email address", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

        if submitted:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                with st.spinner("Signing in…"):
                    ok, msg = login(email, password)
                if ok:
                    st.success(msg)
                    st.session_state["active_page"] = "dashboard"
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center; color:#64748B;'>Don't have an account?</div>",
            unsafe_allow_html=True,
        )
        if st.button("Create Account", use_container_width=True):
            st.session_state["active_page"] = "register"
            st.rerun()

    # Demo credentials box
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🔑 Demo Credentials"):
        st.markdown("""
| Role | Email | Password |
|------|-------|----------|
| Patient | patient@medvision.ai | Password@123 |
| Doctor | doctor@medvision.ai | Password@123 |
| Admin | admin@medvision.ai | Password@123 |
        """)
        st.caption("Demo accounts use the seed data from `database/sample_data.sql`")
