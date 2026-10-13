"""
Doctor Dashboard - overview of patients, appointments, and pending reviews.
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.database import execute_query, execute_write
from app.core.utils import section_header, metric_card, fmt_date, fmt_datetime, status_badge, ai_disclaimer


def show():
    user = require_auth(["doctor"])
    did = user["doctor_id"]

    section_header("🩺 Doctor Dashboard", f"Welcome, Dr. {user['name']}")

    if not did:
        st.warning("Doctor profile not fully set up. Please contact admin.")
        return

    # ── KPI row ───────────────────────────────────────────────────────────────
    try:
        total_patients = execute_query(
            "SELECT COUNT(DISTINCT patient_id) FROM appointments WHERE doctor_id=:did", {"did": did}
        )
        pending_apts = execute_query(
            "SELECT COUNT(*) FROM appointments WHERE doctor_id=:did AND status='requested'", {"did": did}
        )
        confirmed_apts = execute_query(
            "SELECT COUNT(*) FROM appointments WHERE doctor_id=:did AND status='confirmed'", {"did": did}
        )
        pending_reviews = execute_query(
            "SELECT COUNT(*) FROM medical_reports WHERE is_doctor_reviewed=FALSE", {}
        )
    except Exception:
        total_patients = pending_apts = confirmed_apts = pending_reviews = [[0]]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total Patients", str(total_patients[0][0] if total_patients else 0), color="#0EA5E9")
    with c2:
        metric_card("Pending Requests", str(pending_apts[0][0] if pending_apts else 0), color="#F59E0B")
    with c3:
        metric_card("Confirmed Today", str(confirmed_apts[0][0] if confirmed_apts else 0), color="#10B981")
    with c4:
        metric_card("Reports to Review", str(pending_reviews[0][0] if pending_reviews else 0), color="#8B5CF6")

    st.markdown("---")
    col_left, col_right = st.columns([1.4, 1])

    # ── Pending appointment requests ──────────────────────────────────────────
    with col_left:
        st.markdown("#### 📋 Pending Appointment Requests")
        try:
            rows = execute_query(
                """SELECT a.id, a.appointment_date, a.reason, u.full_name, u.phone
                   FROM appointments a
                   JOIN patients p ON a.patient_id = p.id
                   JOIN users u ON p.user_id = u.id
                   WHERE a.doctor_id=:did AND a.status='requested'
                   ORDER BY a.appointment_date""",
                {"did": did},
            )
        except Exception as e:
            rows = []
            st.error(str(e))

        if not rows:
            st.info("No pending requests.")
        else:
            for row in rows:
                aid, apt_dt, reason, pname, phone = row
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 2, 1])
                    with c1:
                        st.markdown(f"**{pname}**")
                        st.caption(f"📅 {fmt_datetime(apt_dt)}")
                        if reason:
                            st.caption(f"Reason: {reason[:60]}")
                    with c2:
                        if phone:
                            st.caption(f"📞 {phone}")
                    with c3:
                        if st.button("✅", key=f"conf_{aid}", help="Confirm"):
                            try:
                                execute_write(
                                    "UPDATE appointments SET status='confirmed', updated_at=NOW() WHERE id=:aid",
                                    {"aid": aid},
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))
                        if st.button("❌", key=f"dec_{aid}", help="Decline"):
                            try:
                                execute_write(
                                    "UPDATE appointments SET status='cancelled', updated_at=NOW() WHERE id=:aid",
                                    {"aid": aid},
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))

    # ── Today's confirmed appointments ────────────────────────────────────────
    with col_right:
        st.markdown("#### 📅 Today's Schedule")
        try:
            from datetime import date
            today = date.today()
            today_rows = execute_query(
                """SELECT a.appointment_date, u.full_name, a.reason, a.status
                   FROM appointments a
                   JOIN patients p ON a.patient_id=p.id
                   JOIN users u ON p.user_id=u.id
                   WHERE a.doctor_id=:did
                     AND DATE(a.appointment_date)=:today
                     AND a.status IN ('confirmed','requested')
                   ORDER BY a.appointment_date""",
                {"did": did, "today": today},
            )
        except Exception as e:
            today_rows = []

        if not today_rows:
            st.info("No appointments today.")
        else:
            for row in today_rows:
                apt_dt, pname, reason, status = row
                color = "#10B981" if status == "confirmed" else "#F59E0B"
                st.markdown(
                    f"<div style='border-left:3px solid {color};padding:6px 10px;margin-bottom:6px;'>"
                    f"<strong>{fmt_datetime(apt_dt)[11:16]}</strong> — {pname}</div>",
                    unsafe_allow_html=True,
                )

    # ── Quick actions ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### ⚡ Quick Actions")
    q1, q2, q3 = st.columns(3)
    with q1:
        if st.button("👥 View All Patients", use_container_width=True):
            st.session_state["active_page"] = "doctor_patients"
            st.rerun()
    with q2:
        if st.button("📅 Manage Appointments", use_container_width=True):
            st.session_state["active_page"] = "doctor_appointments"
            st.rerun()
    with q3:
        if st.button("🤖 AI Chatbot", use_container_width=True):
            st.session_state["active_page"] = "chatbot"
            st.rerun()
