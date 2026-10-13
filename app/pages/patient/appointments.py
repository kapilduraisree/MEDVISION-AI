"""
Appointments - book and manage doctor appointments.
"""
import streamlit as st
from datetime import date, datetime, timedelta
from app.core.auth import require_auth
from app.core.database import execute_query, execute_write
from app.core.utils import section_header, fmt_datetime, status_badge


def show():
    user = require_auth(["patient"])
    pid = user["patient_id"]

    section_header("📅 Appointments", "Book and manage your doctor appointments")

    tab_book, tab_upcoming, tab_past = st.tabs(["📋 Book Appointment", "📅 Upcoming", "🗂️ Past"])

    with tab_book:
        # Load available doctors
        try:
            doctors = execute_query(
                """SELECT d.id, u.full_name, d.specialization, d.hospital_name,
                          d.consultation_fee, d.available_days
                   FROM doctors d JOIN users u ON d.user_id=u.id
                   WHERE d.is_available=TRUE AND u.is_active=TRUE
                   ORDER BY u.full_name""",
                {},
            )
        except Exception as e:
            st.error(f"Could not load doctors: {e}")
            doctors = []

        if not doctors:
            st.info("No doctors available at the moment.")
        else:
            with st.form("appointment_form"):
                doctor_options = {f"Dr. {r[1]} — {r[2] or 'General'} ({r[3] or ''})": r[0] for r in doctors}
                selected_doc_label = st.selectbox("Select Doctor", list(doctor_options.keys()))
                doctor_id = doctor_options[selected_doc_label]

                # Show selected doctor details
                selected = next((r for r in doctors if r[0] == doctor_id), None)
                if selected:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.caption(f"Specialization: {selected[2] or '—'}")
                        st.caption(f"Hospital: {selected[3] or '—'}")
                    with c2:
                        st.caption(f"Fee: ₹{selected[4] or '—'}")
                        st.caption(f"Available: {selected[5] or '—'}")

                apt_date = st.date_input(
                    "Preferred Date",
                    min_value=date.today() + timedelta(days=1),
                    value=date.today() + timedelta(days=1),
                )
                apt_time = st.time_input("Preferred Time")
                reason = st.text_area("Reason for visit", height=80, placeholder="Describe why you want to visit…")
                submitted = st.form_submit_button("📅 Book Appointment", type="primary", use_container_width=True)

            if submitted:
                if not reason.strip():
                    st.error("Please provide a reason for the visit.")
                else:
                    apt_datetime = datetime.combine(apt_date, apt_time)
                    try:
                        execute_write(
                            """INSERT INTO appointments
                               (patient_id, doctor_id, appointment_date, reason, status, created_at)
                               VALUES (:pid,:did,:dt,:reason,'requested',NOW())""",
                            {"pid": pid, "did": doctor_id,
                             "dt": apt_datetime, "reason": reason},
                        )
                        st.success("✅ Appointment request submitted. The doctor will confirm shortly.")
                    except Exception as e:
                        st.error(f"Booking failed: {e}")

    with tab_upcoming:
        _show_appointments(pid, upcoming=True)

    with tab_past:
        _show_appointments(pid, upcoming=False)


def _show_appointments(pid: int, upcoming: bool):
    condition = "a.status NOT IN ('cancelled','completed')" if upcoming else "a.status IN ('completed','cancelled')"
    order = "ASC" if upcoming else "DESC"
    try:
        rows = execute_query(
            f"""SELECT a.id, a.appointment_date, a.reason, a.status,
                       u.full_name, d.specialization, a.notes
                FROM appointments a
                JOIN doctors d ON a.doctor_id = d.id
                JOIN users u ON d.user_id = u.id
                WHERE a.patient_id=:pid AND {condition}
                ORDER BY a.appointment_date {order}""",
            {"pid": pid},
        )
    except Exception as e:
        st.error(str(e))
        return

    if not rows:
        st.info("No appointments found.")
        return

    for row in rows:
        aid, apt_dt, reason, status, doc_name, spec, notes = row
        status = status or "requested"
        color = {"confirmed":"#10B981","requested":"#F59E0B","cancelled":"#EF4444","completed":"#64748B"}.get(status,"#64748B")
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1:
                st.markdown(f"**Dr. {doc_name}** — {spec or 'General'}")
                st.caption(f"📅 {fmt_datetime(apt_dt)}")
                if reason:
                    st.caption(f"Reason: {reason[:80]}")
            with c2:
                st.markdown(
                    f"<span style='color:{color};font-weight:600'>{status_badge(status)}</span>",
                    unsafe_allow_html=True,
                )
                if notes:
                    st.caption(f"📝 {notes}")
            with c3:
                if status in ("requested","confirmed"):
                    if st.button("❌ Cancel", key=f"cancel_{aid}"):
                        try:
                            execute_write(
                                "UPDATE appointments SET status='cancelled' WHERE id=:aid",
                                {"aid": aid},
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
