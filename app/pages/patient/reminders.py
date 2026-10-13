"""
Medicine Reminders - schedule and track medication adherence.
"""
import streamlit as st
from datetime import date, datetime
from app.core.auth import require_auth
from app.core.database import execute_query, execute_write
from app.core.utils import section_header, fmt_date


def show():
    user = require_auth(["patient"])
    pid = user["patient_id"]

    section_header("⏰ Medicine Reminders", "Schedule and track your medications")

    tab_add, tab_active, tab_log = st.tabs(["➕ Add Reminder", "💊 Active Schedules", "📋 Medication Log"])

    with tab_add:
        with st.form("reminder_form"):
            c1, c2 = st.columns(2)
            with c1:
                medicine = st.text_input("Medicine Name *", placeholder="e.g. Metformin 500mg")
                strength = st.text_input("Strength", placeholder="e.g. 500mg, 10mg")
                frequency = st.selectbox("Frequency", [
                    "Once daily","Twice daily","Thrice daily",
                    "Every 4 hours","Every 6 hours","Every 8 hours",
                    "Weekly","As needed"
                ])
            with c2:
                times = st.text_input("Times", placeholder="e.g. 08:00, 14:00, 20:00")
                food_instruction = st.selectbox("Food instruction", [
                    "After food","Before food","With food","No restriction"
                ])
                start_date = st.date_input("Start Date", value=date.today())
                end_date = st.date_input("End Date (optional)")

            instructions = st.text_area("Special Instructions (optional)", height=80)
            submitted = st.form_submit_button("💾 Save Reminder", type="primary", use_container_width=True)

        if submitted:
            if not medicine.strip():
                st.error("Medicine name is required.")
            else:
                try:
                    execute_write(
                        """INSERT INTO medication_schedules
                           (patient_id, medicine_name, strength, frequency, times,
                            start_date, end_date, instructions, before_after_food,
                            is_active, created_at)
                           VALUES (:pid,:med,:str,:freq,:times,:sd,:ed,:inst,:food,TRUE,NOW())""",
                        {"pid": pid, "med": medicine, "str": strength,
                         "freq": frequency, "times": times,
                         "sd": start_date, "ed": end_date if end_date != start_date else None,
                         "inst": instructions, "food": food_instruction},
                    )
                    st.success(f"✅ Reminder set for **{medicine}** — {frequency}")
                except Exception as e:
                    st.error(f"Failed to save reminder: {e}")

    with tab_active:
        try:
            rows = execute_query(
                """SELECT id, medicine_name, strength, frequency, times,
                          start_date, end_date, before_after_food, instructions
                   FROM medication_schedules
                   WHERE patient_id=:pid AND is_active=TRUE
                   ORDER BY created_at DESC""",
                {"pid": pid},
            )
        except Exception as e:
            st.error(f"Could not load schedules: {e}")
            return

        if not rows:
            st.info("No active medication reminders. Use the Add Reminder tab to set one up.")
            return

        for row in rows:
            sid, med, strength, freq, times, sd, ed, food, inst = row
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 2, 1])
                with c1:
                    st.markdown(f"**💊 {med}** {strength or ''}")
                    st.caption(f"{freq}  •  {food or ''}")
                    if times:
                        st.caption(f"⏰ {times}")
                with c2:
                    st.caption(f"From: {fmt_date(sd)}")
                    if ed:
                        st.caption(f"Until: {fmt_date(ed)}")
                    if inst:
                        st.caption(f"📝 {inst}")
                with c3:
                    if st.button("🗑️ Stop", key=f"stop_{sid}"):
                        try:
                            execute_write(
                                "UPDATE medication_schedules SET is_active=FALSE WHERE id=:sid",
                                {"sid": sid},
                            )
                            st.success("Reminder stopped.")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

    with tab_log:
        st.info("Medication log tracks when you mark doses as taken or missed.")
        try:
            rows = execute_query(
                """SELECT ms.medicine_name, ml.scheduled_time, ml.status, ml.taken_at, ml.notes
                   FROM medication_logs ml
                   JOIN medication_schedules ms ON ml.schedule_id = ms.id
                   WHERE ms.patient_id=:pid
                   ORDER BY ml.scheduled_time DESC LIMIT 30""",
                {"pid": pid},
            )
        except Exception as e:
            st.error(f"Could not load log: {e}")
            return

        if not rows:
            st.info("No medication log entries yet.")
            return

        for row in rows:
            med, sched, status, taken, notes = row
            icon = "✅" if status == "taken" else "❌" if status == "missed" else "⏳"
            st.markdown(f"{icon} **{med}** — scheduled {fmt_date(sched)} — {status or 'pending'}")
