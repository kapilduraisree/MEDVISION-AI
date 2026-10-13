"""
Patient Dashboard - overview of health stats, recent activity, quick actions.
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.database import execute_query
from app.core.utils import metric_card, section_header, fmt_date, fmt_datetime, status_badge


def show():
    user = require_auth(["patient"])
    pid = user["patient_id"]
    lang = user["language"]

    section_header("🏠 My Dashboard", f"Welcome back, {user['name']}")

    if not pid:
        st.warning("Patient profile not set up. Please complete your profile.")
        return

    # ── Top KPI row ──────────────────────────────────────────────────────────
    try:
        reports = execute_query(
            "SELECT COUNT(*) FROM medical_reports WHERE patient_id = :pid", {"pid": pid}
        )
        prescriptions = execute_query(
            "SELECT COUNT(*) FROM prescriptions WHERE patient_id = :pid", {"pid": pid}
        )
        reminders = execute_query(
            "SELECT COUNT(*) FROM medication_schedules WHERE patient_id = :pid AND is_active = TRUE",
            {"pid": pid},
        )
        appointments = execute_query(
            "SELECT COUNT(*) FROM appointments WHERE patient_id = :pid AND status NOT IN ('cancelled','completed')",
            {"pid": pid},
        )
        r_count = reports[0][0] if reports else 0
        p_count = prescriptions[0][0] if prescriptions else 0
        rem_count = reminders[0][0] if reminders else 0
        apt_count = appointments[0][0] if appointments else 0
    except Exception:
        r_count = p_count = rem_count = apt_count = 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Medical Reports", str(r_count), color="#0EA5E9")
    with c2:
        metric_card("Prescriptions", str(p_count), color="#8B5CF6")
    with c3:
        metric_card("Active Reminders", str(rem_count), color="#10B981")
    with c4:
        metric_card("Appointments", str(apt_count), color="#F59E0B")

    st.markdown("---")

    col_left, col_right = st.columns([1.3, 1])

    # ── Recent reports ────────────────────────────────────────────────────────
    with col_left:
        st.markdown("#### 📄 Recent Reports")
        try:
            rows = execute_query(
                """SELECT id, report_type, lab_name, report_date, summary
                   FROM medical_reports WHERE patient_id = :pid
                   ORDER BY created_at DESC LIMIT 5""",
                {"pid": pid},
            )
            if rows:
                for row in rows:
                    with st.container(border=True):
                        c_a, c_b = st.columns([3, 1])
                        with c_a:
                            st.markdown(f"**{row[1] or 'Medical Report'}**")
                            st.caption(f"{row[2] or '—'}  •  {fmt_date(row[3])}")
                        with c_b:
                            if st.button("View", key=f"rpt_{row[0]}"):
                                st.session_state["view_report_id"] = row[0]
                                st.session_state["active_page"] = "reports"
                                st.rerun()
            else:
                st.info("No reports uploaded yet.")
        except Exception as e:
            st.warning(f"Could not load reports: {e}")

    # ── Upcoming reminders & appointments ─────────────────────────────────────
    with col_right:
        st.markdown("#### 💊 Today's Medications")
        try:
            meds = execute_query(
                """SELECT medicine_name, strength, times, frequency
                   FROM medication_schedules
                   WHERE patient_id = :pid AND is_active = TRUE LIMIT 5""",
                {"pid": pid},
            )
            if meds:
                for m in meds:
                    st.markdown(
                        f"🔔 **{m[0]}** {m[1] or ''} — {m[2] or m[3] or ''}"
                    )
            else:
                st.info("No active medication reminders.")
        except Exception as e:
            st.warning(f"Could not load reminders: {e}")

        st.markdown("#### 📅 Upcoming Appointments")
        try:
            apts = execute_query(
                """SELECT a.appointment_date, d.specialization, u.full_name
                   FROM appointments a
                   JOIN doctors d ON a.doctor_id = d.id
                   JOIN users u ON d.user_id = u.id
                   WHERE a.patient_id = :pid AND a.status NOT IN ('cancelled','completed')
                   ORDER BY a.appointment_date LIMIT 3""",
                {"pid": pid},
            )
            if apts:
                for apt in apts:
                    st.markdown(f"📆 **{fmt_datetime(apt[0])}** — Dr. {apt[2]} ({apt[1] or 'General'})")
            else:
                st.info("No upcoming appointments.")
        except Exception as e:
            st.warning(f"Could not load appointments: {e}")

    # ── Quick actions ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### ⚡ Quick Actions")
    q1, q2, q3, q4, q5 = st.columns(5)
    actions = [
        ("📤 Upload Report", "reports"),
        ("💊 Add Reminder", "reminders"),
        ("🩺 Check Symptoms", "symptoms"),
        ("🤖 AI Chatbot", "chatbot"),
        ("🚨 Emergency", "emergency"),
    ]
    for col, (label, page) in zip([q1, q2, q3, q4, q5], actions):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state["active_page"] = page
                st.rerun()
