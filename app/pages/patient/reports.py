"""
Patient Reports - upload blood reports, view OCR extraction and AI explanations.
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.database import execute_query, execute_write
from app.core.utils import section_header, save_uploaded_file, ai_disclaimer, status_badge, fmt_date
from app.services.ai.ocr_service import extract_text_from_bytes, parse_lab_values, categorize_value
from app.services.ai.report_explainer import explain_test_value, generate_doctor_questions, generate_report_summary


def show():
    user = require_auth(["patient", "doctor"])
    pid = user["patient_id"]
    lang = user["language"]

    section_header("📄 Medical Reports", "Upload and analyse your lab reports with AI")

    tab_upload, tab_history = st.tabs(["📤 Upload New Report", "📋 Report History"])

    # ── Upload tab ────────────────────────────────────────────────────────────
    with tab_upload:
        with st.form("report_upload_form"):
            col1, col2 = st.columns(2)
            with col1:
                report_type = st.selectbox("Report Type", [
                    "Blood Test (CBC)", "Blood Sugar / Glucose",
                    "Lipid Profile", "Liver Function Test (LFT)",
                    "Kidney Function Test (KFT)", "Thyroid Profile",
                    "Urine Analysis", "X-Ray / Scan Report", "Other",
                ])
                lab_name = st.text_input("Lab / Hospital Name")
            with col2:
                report_date = st.date_input("Report Date")
                doctor_name = st.text_input("Referring Doctor (optional)")

            uploaded = st.file_uploader(
                "Upload Report (Image or PDF)",
                type=["jpg","jpeg","png","pdf","bmp","tiff"],
            )
            submitted = st.form_submit_button("🔍 Analyse Report", type="primary", use_container_width=True)

        if submitted:
            if not uploaded:
                st.error("Please upload a file.")
            else:
                with st.spinner("Running OCR and AI analysis…"):
                    file_bytes = uploaded.read()
                    ocr = extract_text_from_bytes(file_bytes, uploaded.name)
                    raw_text = ocr.get("text", "")
                    confidence = ocr.get("confidence", 0.0)

                    file_path = save_uploaded_file(uploaded, "reports") or ""
                    values = parse_lab_values(raw_text)
                    for v in values:
                        v["status"] = categorize_value(v.get("result",""), v.get("reference_range_text",""))
                        v["explanation"] = explain_test_value(
                            v.get("test_name",""), v.get("result",""),
                            v.get("unit",""), v.get("reference_range_text",""),
                            v.get("status","unknown"), lang,
                        )

                    summary = generate_report_summary(values, lang)

                try:
                    execute_write(
                        """INSERT INTO medical_reports
                           (patient_id, report_type, lab_name, doctor_name, report_date,
                            file_path, original_filename, ocr_raw_text, ocr_confidence,
                            summary, created_at)
                           VALUES (:pid,:rt,:lab,:doc,:rd,:fp,:fn,:ocr,:conf,:summ,NOW())""",
                        {"pid": pid, "rt": report_type, "lab": lab_name,
                         "doc": doctor_name, "rd": report_date,
                         "fp": file_path, "fn": uploaded.name,
                         "ocr": raw_text, "conf": confidence, "summ": summary},
                    )
                    rows = execute_query(
                        "SELECT id FROM medical_reports WHERE patient_id=:pid ORDER BY created_at DESC LIMIT 1",
                        {"pid": pid}
                    )
                    report_id = rows[0][0] if rows else None
                    if report_id:
                        for v in values:
                            execute_write(
                                """INSERT INTO report_values
                                   (report_id, test_name, result, unit,
                                    reference_range_text, status, explanation, created_at)
                                   VALUES (:rid,:tn,:res,:unit,:ref,:status,:exp,NOW())""",
                                {"rid": report_id, "tn": v["test_name"],
                                 "res": v["result"], "unit": v["unit"],
                                 "ref": v["reference_range_text"],
                                 "status": v["status"], "exp": v["explanation"]},
                            )
                except Exception as db_err:
                    st.warning(f"Report saved locally but DB insert failed: {db_err}")

                # Display results
                st.success(f"✅ OCR complete — confidence: {confidence*100:.0f}%")
                if confidence < 0.6:
                    st.warning("⚠️ Low OCR confidence. Results may need manual review.")

                ai_disclaimer(lang)
                st.markdown("### 📊 Report Summary")
                st.info(summary)

                st.markdown("### 🔬 Test Values")
                _render_report_values(values, lang)

                questions = generate_doctor_questions(values, lang)
                if questions:
                    with st.expander("❓ Questions to ask your doctor"):
                        for q in questions:
                            st.markdown(f"• {q}")

    # ── History tab ───────────────────────────────────────────────────────────
    with tab_history:
        try:
            rows = execute_query(
                """SELECT id, report_type, lab_name, report_date, ocr_confidence, summary, created_at
                   FROM medical_reports WHERE patient_id=:pid
                   ORDER BY created_at DESC""",
                {"pid": pid},
            )
        except Exception as e:
            st.error(f"Could not load reports: {e}")
            return

        if not rows:
            st.info("No reports uploaded yet. Use the Upload tab to add your first report.")
            return

        for row in rows:
            rid, rtype, lab, rdate, conf, summary, created = row
            with st.expander(f"📄 {rtype or 'Report'} — {fmt_date(rdate)}  |  {lab or ''}"):
                st.caption(f"Uploaded: {fmt_date(created)}  •  OCR confidence: {conf*100:.0f}%" if conf else "")
                if summary:
                    st.markdown(summary)
                try:
                    vals = execute_query(
                        """SELECT test_name, result, unit, reference_range_text, status, explanation
                           FROM report_values WHERE report_id=:rid ORDER BY id""",
                        {"rid": rid},
                    )
                    if vals:
                        _render_db_values(vals, lang)
                except Exception:
                    pass


def _render_report_values(values: list, lang: str):
    for v in values:
        status = v.get("status","unknown")
        color = {"normal":"#10B981","attention":"#F59E0B","abnormal":"#EF4444"}.get(status,"#64748B")
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([2.5, 1, 1.5, 1.5])
            with c1:
                st.markdown(f"**{v.get('test_name','')}**")
            with c2:
                st.markdown(f"`{v.get('result','')} {v.get('unit','')}`")
            with c3:
                st.caption(f"Ref: {v.get('reference_range_text','')}")
            with c4:
                st.markdown(
                    f"<span style='color:{color};font-weight:600'>{status_badge(status)}</span>",
                    unsafe_allow_html=True
                )
            if v.get("explanation"):
                with st.expander("📖 Explanation"):
                    st.markdown(v["explanation"])


def _render_db_values(rows, lang: str):
    for row in rows:
        tname, result, unit, ref, status, expl = row
        status = status or "unknown"
        color = {"normal":"#10B981","attention":"#F59E0B","abnormal":"#EF4444"}.get(status,"#64748B")
        c1, c2, c3, c4 = st.columns([2.5, 1, 1.5, 1.5])
        with c1:
            st.markdown(f"**{tname}**")
        with c2:
            st.markdown(f"`{result} {unit or ''}`")
        with c3:
            st.caption(f"Ref: {ref or ''}")
        with c4:
            st.markdown(
                f"<span style='color:{color};font-weight:600'>{status_badge(status)}</span>",
                unsafe_allow_html=True
            )
