"""
Admin Dashboard - system-wide analytics.
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.database import execute_query
from app.core.utils import section_header, metric_card

try:
    import pandas as pd
    import plotly.express as px
    PLOT_OK = True
except ImportError:
    PLOT_OK = False


def show():
    user = require_auth(["admin"])
    section_header("🛡️ Admin Dashboard", "System overview and analytics")

    # ── System KPIs ───────────────────────────────────────────────────────────
    try:
        total_users = execute_query("SELECT COUNT(*) FROM users", {})
        total_patients = execute_query("SELECT COUNT(*) FROM patients", {})
        total_doctors = execute_query("SELECT COUNT(*) FROM doctors", {})
        total_reports = execute_query("SELECT COUNT(*) FROM medical_reports", {})
        total_appointments = execute_query("SELECT COUNT(*) FROM appointments", {})
        total_medicines = execute_query("SELECT COUNT(*) FROM medicines", {})
    except Exception as e:
        st.error(f"Could not load analytics: {e}")
        return

    def _n(rows):
        return rows[0][0] if rows else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Total Users", str(_n(total_users)), color="#0EA5E9")
        metric_card("Medical Reports", str(_n(total_reports)), color="#8B5CF6")
    with c2:
        metric_card("Patients", str(_n(total_patients)), color="#10B981")
        metric_card("Appointments", str(_n(total_appointments)), color="#F59E0B")
    with c3:
        metric_card("Doctors", str(_n(total_doctors)), color="#06B6D4")
        metric_card("Medicine Records", str(_n(total_medicines)), color="#EC4899")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    # ── User registrations over time ──────────────────────────────────────────
    with col_left:
        st.markdown("#### 📈 User Registrations (Last 30 Days)")
        if PLOT_OK:
            try:
                rows = execute_query(
                    """SELECT DATE(created_at) as reg_date, COUNT(*) as count
                       FROM users WHERE created_at >= NOW() - INTERVAL '30 days'
                       GROUP BY DATE(created_at) ORDER BY reg_date""",
                    {},
                )
                if rows:
                    df = pd.DataFrame(rows, columns=["Date","Registrations"])
                    fig = px.bar(df, x="Date", y="Registrations", template="plotly_dark",
                                 color_discrete_sequence=["#0EA5E9"])
                    fig.update_layout(plot_bgcolor="#0F172A", paper_bgcolor="#0F172A", font_color="#F1F5F9")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No registration data in the last 30 days.")
            except Exception as e:
                st.warning(str(e))
        else:
            st.info("Install plotly for charts: `pip install plotly`")

    # ── Appointment status breakdown ──────────────────────────────────────────
    with col_right:
        st.markdown("#### 📊 Appointment Status Breakdown")
        if PLOT_OK:
            try:
                rows = execute_query(
                    "SELECT status, COUNT(*) FROM appointments GROUP BY status", {}
                )
                if rows:
                    df2 = pd.DataFrame(rows, columns=["Status","Count"])
                    fig2 = px.pie(df2, values="Count", names="Status", template="plotly_dark",
                                  color_discrete_sequence=px.colors.qualitative.Set2)
                    fig2.update_layout(plot_bgcolor="#0F172A", paper_bgcolor="#0F172A", font_color="#F1F5F9")
                    st.plotly_chart(fig2, use_container_width=True)
            except Exception as e:
                st.warning(str(e))

    # ── Recent activity ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🕐 Recent Audit Activity")
    try:
        audit = execute_query(
            """SELECT al.action, al.entity_type, al.status, al.created_at, u.full_name
               FROM audit_logs al
               LEFT JOIN users u ON al.user_id = u.id
               ORDER BY al.created_at DESC LIMIT 10""",
            {},
        )
        if audit:
            for row in audit:
                action, entity, status, created, uname = row
                icon = "✅" if status == "success" else "❌"
                st.markdown(f"{icon} **{action}** on {entity or '—'} by {uname or 'System'} — {str(created)[:16]}")
        else:
            st.info("No audit logs yet.")
    except Exception as e:
        st.warning(str(e))

    # ── Quick admin actions ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### ⚡ Admin Actions")
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        if st.button("👥 Manage Users", use_container_width=True):
            st.session_state["active_page"] = "admin_users"
            st.rerun()
    with q2:
        if st.button("👨‍⚕️ Manage Doctors", use_container_width=True):
            st.session_state["active_page"] = "admin_doctors"
            st.rerun()
    with q3:
        if st.button("💊 Manage Medicines", use_container_width=True):
            st.session_state["active_page"] = "admin_medicines"
            st.rerun()
    with q4:
        if st.button("📋 Audit Logs", use_container_width=True):
            st.session_state["active_page"] = "admin_audit"
            st.rerun()
