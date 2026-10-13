"""
MedVision AI – Main Streamlit Application Entry Point
Single-file router: handles auth state, sidebar navigation, and page dispatch.
"""
import streamlit as st

st.set_page_config(
    page_title="MedVision AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports (after set_page_config) ──────────────────────────────────────────
from app.core.auth import is_authenticated, current_user, logout
from app.core.database import test_connection
from app.core.config import settings

# Auth pages
from app.pages import login, register

# Patient pages
from app.pages.patient import (
    dashboard as patient_dashboard,
    reports, symptoms, prescriptions, medicines,
    drug_interactions, reminders, health_trends,
    ai_summary, chatbot, appointments as patient_appointments,
    locker, family, emergency, pharmacy_bills, profile,
    rag_chatbot, live_drug_lookup,
)

# Doctor pages
from app.pages.doctor import (
    dashboard as doctor_dashboard,
    patients as doctor_patients,
    appointments as doctor_appointments,
)

# Admin pages
from app.pages.admin import (
    dashboard as admin_dashboard,
    users as admin_users,
    medicines as admin_medicines,
    audit_logs,
    doctors as admin_doctors,
)


# ── Navigation config ─────────────────────────────────────────────────────────
PATIENT_NAV = [
    ("🏠 Dashboard",          "dashboard"),
    ("👤 My Profile",          "profile"),
    ("🩺 Symptoms",            "symptoms"),
    ("📄 Medical Reports",     "reports"),
    ("📋 Prescriptions",       "prescriptions"),
    ("💊 Medicines",           "medicines"),
    ("⚗️ Drug Interactions",   "drug_interactions"),
    ("🌐 Live Drug Lookup",    "live_drug_lookup"),
    ("⏰ Reminders",           "reminders"),
    ("📈 Health Trends",       "health_trends"),
    ("🤖 AI Health Summary",   "ai_summary"),
    ("🧠 RAG Health Assistant","rag_chatbot"),
    ("💬 AI Chatbot",          "chatbot"),
    ("📅 Appointments",        "appointments"),
    ("🧾 Pharmacy Bills",      "pharmacy_bills"),
    ("🔒 Medical Locker",      "locker"),
    ("👨‍👩‍👧 Family Profiles",    "family"),
    ("🚨 Emergency",           "emergency"),
]

DOCTOR_NAV = [
    ("🩺 Dashboard",          "dashboard"),
    ("👥 My Patients",        "doctor_patients"),
    ("📅 Appointments",       "doctor_appointments"),
    ("💊 Medicines",          "medicines"),
    ("🌐 Live Drug Lookup",   "live_drug_lookup"),
    ("⚗️ Drug Interactions",  "drug_interactions"),
    ("💬 AI Chatbot",         "chatbot"),
]

ADMIN_NAV = [
    ("🛡️ Dashboard",         "dashboard"),
    ("👥 Users",              "admin_users"),
    ("👨‍⚕️ Doctors",           "admin_doctors"),
    ("💊 Medicines",          "admin_medicines"),
    ("📋 Audit Logs",         "admin_audit"),
    ("💬 AI Chatbot",         "chatbot"),
]

PAGE_ROUTER = {
    # patient
    "dashboard":        patient_dashboard.show,
    "profile":          profile.show,
    "symptoms":         symptoms.show,
    "reports":          reports.show,
    "prescriptions":    prescriptions.show,
    "medicines":        medicines.show,
    "drug_interactions":drug_interactions.show,
    "reminders":        reminders.show,
    "health_trends":    health_trends.show,
    "ai_summary":       ai_summary.show,
    "chatbot":          chatbot.show,
    "rag_chatbot":      rag_chatbot.show,
    "live_drug_lookup": live_drug_lookup.show,
    "appointments":     patient_appointments.show,
    "pharmacy_bills":   pharmacy_bills.show,
    "locker":           locker.show,
    "family":           family.show,
    "emergency":        emergency.show,
    # doctor
    "doctor_patients":      doctor_patients.show,
    "doctor_appointments":  doctor_appointments.show,
    # admin
    "admin_users":      admin_users.show,
    "admin_doctors":    admin_doctors.show,
    "admin_medicines":  admin_medicines.show,
    "admin_audit":      audit_logs.show,
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def _nav_for_role(role: str) -> list:
    return {"doctor": DOCTOR_NAV, "admin": ADMIN_NAV}.get(role, PATIENT_NAV)


def _default_page(role: str) -> str:
    return "dashboard"


def _render_sidebar(user: dict):
    with st.sidebar:
        # Logo / title
        st.markdown(
            """
            <div style="text-align:center;padding:1rem 0 0.5rem 0;">
                <span style="font-size:2rem;">🏥</span>
                <div style="color:#0EA5E9;font-size:1.2rem;font-weight:700;">MedVision AI</div>
                <div style="color:#64748B;font-size:0.75rem;">v2.0.0</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""<div style="background:#1E293B;border-radius:8px;padding:8px 12px;
                           margin-bottom:12px;font-size:0.85rem;">
                👤 <strong>{user['name']}</strong><br>
                <span style="color:#64748B;">{user['email']}</span><br>
                <span style="color:#0EA5E9;text-transform:capitalize;">{user['role']}</span>
            </div>""",
            unsafe_allow_html=True,
        )

        st.markdown("---")

        nav = _nav_for_role(user["role"])
        active = st.session_state.get("active_page", _default_page(user["role"]))

        for label, page_key in nav:
            is_active = (active == page_key)
            btn_style = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{page_key}",
                         use_container_width=True, type=btn_style):
                st.session_state["active_page"] = page_key
                st.rerun()

        st.markdown("---")

        # DB status indicator
        if st.session_state.get("db_ok") is None:
            st.session_state["db_ok"] = test_connection()
        db_icon = "🟢" if st.session_state["db_ok"] else "🔴"
        st.caption(f"{db_icon} Database {'Connected' if st.session_state['db_ok'] else 'Disconnected'}")

        # Language toggle
        lang = user.get("language", "en")
        new_lang = st.selectbox(
            "🌐 Language",
            ["en", "ta"],
            index=0 if lang == "en" else 1,
            format_func=lambda x: "English" if x == "en" else "தமிழ் Tamil",
            key="lang_select",
        )
        if new_lang != lang:
            st.session_state["language"] = new_lang
            st.rerun()

        # Logout
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Sign Out", use_container_width=True):
            logout()
            st.rerun()

        # AI disclaimer reminder
        st.markdown(
            "<div style='color:#475569;font-size:0.65rem;margin-top:8px;text-align:center;'>"
            "AI outputs are informational only.<br>Always consult a qualified doctor.</div>",
            unsafe_allow_html=True,
        )


def _render_page(user: dict):
    role = user["role"]
    active = st.session_state.get("active_page", _default_page(role))

    # Redirect doctor/admin "dashboard" to their own page
    if active == "dashboard":
        if role == "doctor":
            doctor_dashboard.show()
            return
        elif role == "admin":
            admin_dashboard.show()
            return
        else:
            patient_dashboard.show()
            return

    page_fn = PAGE_ROUTER.get(active)
    if page_fn:
        page_fn()
    else:
        st.error(f"Page '{active}' not found.")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    # Initialise session state defaults
    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "login"

    if not is_authenticated():
        page = st.session_state.get("active_page", "login")
        if page == "register":
            register.show()
        else:
            login.show()
        return

    user = current_user()

    # First-time post-login: set default page by role
    if st.session_state.get("active_page") in ("login", "register"):
        st.session_state["active_page"] = _default_page(user["role"])

    _render_sidebar(user)
    _render_page(user)


if __name__ == "__main__":
    main()
