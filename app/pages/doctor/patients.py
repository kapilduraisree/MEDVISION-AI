"""
Doctor – Patient Management
View patients, their reports, and add clinical notes.
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.database import execute_query, execute_write
from app.core.utils import section_header, fmt_date, fmt_datetime, ai_disclaimer, status_badge


def show():
    user = require_auth(["doctor"])
    did = user["doctor_id"]

    section_header("👥 My Patients", "Review patient data, reports, and add clinical notes")

    # ── Patient list ──────────────────────────────────────────────────────────
    try:
        patients = execute_query(
            """SELECT DISTINCT p.id, u.full_name, u.email, u.phone,
                      p.date_of_birth, p.gender, p.blood_group,
                      p.chronic_conditions, p.known_allergies
               FROM appointments a
               JOIN patients p ON a.patient_id = p.id
               JOIN users u ON p.user_id = u.id
               WHERE a.doctor_id=:did
               ORDER BY u.full_name""",
            {"did": did},
        )
    except Exception as e:
        st.error(f"Could not load patients: {e}")
        return

    if not patients:
        st.info("No patients yet. Patients will appear here after appointments are booked.")
        return

    # Search
    search = st.text_input("🔍 Search patients by name", placeholder="Type to filter…")
    if search:
        patients = [p for p in patients if search.lower() in (p[1] or "").lower()]

    st.caption(f"{len(patients)} patient(s)")

    for row in patients:
        pid, name, email, phone, dob, gender, bg, conditions, allergies = row

        with st.expander(f"👤 {name}  —  {gender or ''}  {bg or ''}"):
            tab_overview, tab_reports, tab_notes = st.tabs(["Overview", "Reports", "Add Note"])

            with tab_overview:
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("DOB", fmt_date(dob) if dob else "—")
                    st.metric("Gender", gender or "—")
                with c2:
                    st.metric("Blood Group", bg or "—")
                    if phone:
                        st.metric("Phone", phone)
                with c3:
                    if email:
                        st.caption(f"📧 {email}")

                if conditions:
                    st.markdown(f"**🏥 Conditions:** {conditions}")
                if allergies:
                    st.warning(f"⚠️ **Allergies:** {allergies}")

                # Recent symptoms
                try:
                    symptoms = execute_query(
                        """SELECT description, severity, created_at
                           FROM symptoms WHERE patient_id=:pid
                           ORDER BY created_at DESC LIMIT 3""",
                        {"pid": pid},
                    )
                    if symptoms:
                        st.markdown("**Recent Symptoms:**")
                        for s in symptoms:
                            st.markdown(f"• {s[0][:100]} _(_{s[1] or 'N/A'}_, {fmt_date(s[2])})_")
                except Exception:
                    pass

            with tab_reports:
                try:
                    reports = execute_query(
                        """SELECT id, report_type, lab_name, report_date,
                                  ocr_confidence, summary, is_doctor_reviewed
                           FROM medical_reports WHERE patient_id=:pid
                           ORDER BY created_at DESC LIMIT 10""",
                        {"pid": pid},
                    )
                except Exception as e:
                    st.error(str(e))
                    reports = []

                if not reports:
                    st.info("No reports uploaded by this patient.")
                else:
                    for rpt in reports:
                        rid, rtype, lab, rdate, conf, summary, reviewed = rpt
                        reviewed_label = "✅ Reviewed" if reviewed else "⏳ Pending review"
                        with st.container(border=True):
                            c1, c2, c3 = st.columns([3, 2, 1])
                            with c1:
                                st.markdown(f"**{rtype or 'Report'}**  —  {lab or ''}")
                                st.caption(f"Date: {fmt_date(rdate)}  •  OCR: {conf*100:.0f}%" if conf else fmt_date(rdate))
                            with c2:
                                st.caption(reviewed_label)
                            with c3:
                                if not reviewed:
                                    if st.button("✅ Mark Reviewed", key=f"rev_{rid}"):
                                        try:
                                            execute_write(
                                                "UPDATE medical_reports SET is_doctor_reviewed=TRUE WHERE id=:rid",
                                                {"rid": rid},
                                            )
                                            st.rerun()
                                        except Exception as e:
                                            st.error(str(e))

                            if summary:
                                with st.expander("📋 AI Summary"):
                                    st.markdown(summary)
                                    ai_disclaimer(user["language"])

                            # Report values
                            try:
                                vals = execute_query(
                                    """SELECT test_name, result, unit, reference_range_text, status
                                       FROM report_values WHERE report_id=:rid""",
                                    {"rid": rid},
                                )
                                if vals:
                                    for v in vals:
                                        tname, result, unit, ref, status = v
                                        status = status or "unknown"
                                        color = {"normal":"#10B981","attention":"#F59E0B","abnormal":"#EF4444"}.get(status,"#64748B")
                                        st.markdown(
                                            f"&nbsp;&nbsp;• **{tname}**: `{result} {unit or ''}` "
                                            f"<span style='color:{color}'>{status_badge(status)}</span>",
                                            unsafe_allow_html=True,
                                        )
                            except Exception:
                                pass

            with tab_notes:
                st.markdown("#### ✏️ Add Clinical Note")
                st.info("Clinical notes are added to the patient record. Always follow your institution's guidelines.")
                with st.form(f"note_form_{pid}"):
                    note_text = st.text_area("Clinical Note", height=120,
                                             placeholder="Observations, recommendations, follow-up…")
                    follow_up = st.date_input("Follow-up Date (optional)")
                    is_approved = st.checkbox("Mark as approved summary")
                    note_submit = st.form_submit_button("💾 Save Note", type="primary")

                if note_submit:
                    if not note_text.strip():
                        st.error("Note cannot be empty.")
                    else:
                        try:
                            execute_write(
                                """INSERT INTO doctor_notes
                                   (doctor_id, patient_id, note_text, follow_up_date,
                                    is_approved_summary, created_at)
                                   VALUES (:did,:pid,:note,:fu,:approved,NOW())""",
                                {"did": did, "pid": pid, "note": note_text,
                                 "fu": follow_up, "approved": is_approved},
                            )
                            st.success("✅ Note saved.")
                        except Exception as e:
                            st.error(str(e))

                # Existing notes
                try:
                    existing_notes = execute_query(
                        """SELECT note_text, follow_up_date, is_approved_summary, created_at
                           FROM doctor_notes WHERE doctor_id=:did AND patient_id=:pid
                           ORDER BY created_at DESC LIMIT 5""",
                        {"did": did, "pid": pid},
                    )
                    if existing_notes:
                        st.markdown("**Previous Notes:**")
                        for n in existing_notes:
                            note, fu, approved, created = n
                            icon = "✅" if approved else "📝"
                            st.markdown(
                                f"{icon} _{fmt_date(created)}_ — {note[:200]}"
                                + (f"  •  Follow-up: {fmt_date(fu)}" if fu else "")
                            )
                except Exception:
                    pass
