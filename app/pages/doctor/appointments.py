"""
Doctor – Appointments Management
"""
import streamlit as st
from datetime import date
from app.core.auth import require_auth
from app.core.database import execute_query, execute_write
from app.core.utils import section_header, fmt_datetime, status_badge


def show():
    user = require_auth(["doctor"])
    did = user["doctor_id"]

    section_header("📅 Appointments", "Manage your appointment schedule")

    tab_pending, tab_today, tab_all = st.tabs([
        "⏳ Pending Requests", "📅 Today", "🗂️ All Appointments"
    ])

    with tab_pending:
        _show_appointments(did, status_filter="requested", label="No pending requests.")

    with tab_today:
        _show_today(did)

    with tab_all:
        status_sel = st.selectbox("Filter by status", ["all","requested","confirmed","completed","cancelled"])
        _show_appointments(did, status_filter=status_sel if status_sel != "all" else None, label="No appointments found.")


def _show_today(did: int):
    try:
        today = date.today()
        rows = execute_query(
            """SELECT a.id, a.appointment_date, a.reason, a.status, a.notes,
                      u.full_name, u.phone
               FROM appointments a
               JOIN patients p ON a.patient_id=p.id
               JOIN users u ON p.user_id=u.id
               WHERE a.doctor_id=:did AND DATE(a.appointment_date)=:today
               ORDER BY a.appointment_date""",
            {"did": did, "today": today},
        )
    except Exception as e:
        st.error(str(e))
        return

    if not rows:
        st.info("No appointments today.")
        return

    for row in rows:
        _render_appointment_card(row, did, show_complete=True)


def _show_appointments(did: int, status_filter: str = None, label: str = "No appointments."):
    try:
        if status_filter:
            rows = execute_query(
                """SELECT a.id, a.appointment_date, a.reason, a.status, a.notes,
                          u.full_name, u.phone
                   FROM appointments a
                   JOIN patients p ON a.patient_id=p.id
                   JOIN users u ON p.user_id=u.id
                   WHERE a.doctor_id=:did AND a.status=:status
                   ORDER BY a.appointment_date DESC""",
                {"did": did, "status": status_filter},
            )
        else:
            rows = execute_query(
                """SELECT a.id, a.appointment_date, a.reason, a.status, a.notes,
                          u.full_name, u.phone
                   FROM appointments a
                   JOIN patients p ON a.patient_id=p.id
                   JOIN users u ON p.user_id=u.id
                   WHERE a.doctor_id=:did
                   ORDER BY a.appointment_date DESC LIMIT 50""",
                {"did": did},
            )
    except Exception as e:
        st.error(str(e))
        return

    if not rows:
        st.info(label)
        return

    for row in rows:
        _render_appointment_card(row, did, show_complete=(status_filter == "confirmed"))


def _render_appointment_card(row, did: int, show_complete: bool = False):
    aid, apt_dt, reason, status, notes, pname, phone = row
    status = status or "requested"
    color = {"confirmed":"#10B981","requested":"#F59E0B","cancelled":"#EF4444","completed":"#0EA5E9"}.get(status,"#64748B")

    with st.container(border=True):
        c1, c2, c3 = st.columns([3, 2, 2])
        with c1:
            st.markdown(f"**{pname}**")
            st.caption(f"📅 {fmt_datetime(apt_dt)}")
            if reason:
                st.caption(f"Reason: {reason[:80]}")
        with c2:
            st.markdown(
                f"<span style='color:{color};font-weight:600'>{status_badge(status)}</span>",
                unsafe_allow_html=True,
            )
            if phone:
                st.caption(f"📞 {phone}")
        with c3:
            if status == "requested":
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✅ Confirm", key=f"ac_conf_{aid}"):
                        try:
                            execute_write(
                                "UPDATE appointments SET status='confirmed', updated_at=NOW() WHERE id=:aid",
                                {"aid": aid},
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                with col_b:
                    if st.button("❌ Decline", key=f"ac_dec_{aid}"):
                        try:
                            execute_write(
                                "UPDATE appointments SET status='cancelled', updated_at=NOW() WHERE id=:aid",
                                {"aid": aid},
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

            elif status == "confirmed" and show_complete:
                if st.button("✅ Complete", key=f"ac_done_{aid}"):
                    try:
                        execute_write(
                            "UPDATE appointments SET status='completed', updated_at=NOW() WHERE id=:aid",
                            {"aid": aid},
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

        # Doctor notes inline
        if notes:
            st.caption(f"📝 {notes}")
        with st.expander("💬 Add / View Notes", expanded=False):
            with st.form(f"apt_note_{aid}"):
                note_text = st.text_area("Note", value=notes or "", height=70)
                if st.form_submit_button("Save Note"):
                    try:
                        execute_write(
                            "UPDATE appointments SET notes=:notes WHERE id=:aid",
                            {"notes": note_text, "aid": aid},
                        )
                        st.success("Note saved.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
