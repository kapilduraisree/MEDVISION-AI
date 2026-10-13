"""
Prescription Analyzer - upload and extract medicine info from prescription images.
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.database import execute_query, execute_write
from app.core.utils import section_header, save_uploaded_file, ai_disclaimer, fmt_date
from app.services.ai.prescription_analyzer import analyze_prescription


def show():
    user = require_auth(["patient"])
    pid = user["patient_id"]
    lang = user["language"]

    section_header("📋 Prescription Analyzer", "Extract and verify medicines from your prescriptions")
    ai_disclaimer(lang)

    tab_upload, tab_history = st.tabs(["📤 Analyze Prescription", "📋 My Prescriptions"])

    with tab_upload:
        with st.form("rx_form"):
            uploaded = st.file_uploader(
                "Upload Prescription Image or PDF",
                type=["jpg","jpeg","png","pdf"],
            )
            notes = st.text_area("Additional Notes (optional)", placeholder="Any notes about this prescription…")
            submitted = st.form_submit_button("🔍 Analyze Prescription", type="primary", use_container_width=True)

        if submitted:
            if not uploaded:
                st.error("Please upload a prescription file.")
            else:
                with st.spinner("Extracting medicines from prescription…"):
                    file_bytes = uploaded.read()
                    result = analyze_prescription(file_bytes=file_bytes, filename=uploaded.name)

                file_path = save_uploaded_file(uploaded, "prescriptions") or ""
                medicines = result.get("medicines", [])
                ocr_text = result.get("ocr_text", "")
                confidence = result.get("confidence", 0.75)

                try:
                    execute_write(
                        """INSERT INTO prescriptions
                           (patient_id, file_path, original_filename, ocr_raw_text,
                            ocr_confidence, notes, created_at)
                           VALUES (:pid,:fp,:fn,:ocr,:conf,:notes,NOW())""",
                        {"pid": pid, "fp": file_path, "fn": uploaded.name,
                         "ocr": ocr_text, "conf": confidence, "notes": notes},
                    )
                    rows = execute_query(
                        "SELECT id FROM prescriptions WHERE patient_id=:pid ORDER BY created_at DESC LIMIT 1",
                        {"pid": pid}
                    )
                    rx_id = rows[0][0] if rows else None
                    if rx_id:
                        for m in medicines:
                            execute_write(
                                """INSERT INTO prescription_items
                                   (prescription_id, medicine_name, strength,
                                    dosage_instruction, frequency, created_at)
                                   VALUES (:rxid,:name,:str,:dos,:freq,NOW())""",
                                {"rxid": rx_id, "name": m.get("name",""),
                                 "str": m.get("strength",""), "dos": m.get("dosage",""),
                                 "freq": m.get("frequency","")},
                            )
                except Exception as e:
                    st.warning(f"Saved locally but DB error: {e}")

                st.success(f"✅ Analysis complete — OCR confidence: {confidence*100:.0f}%")
                st.markdown("### 💊 Extracted Medicines")

                if medicines:
                    for i, med in enumerate(medicines):
                        with st.container(border=True):
                            c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1.5])
                            with c1:
                                st.markdown(f"**{med.get('name','')}**")
                            with c2:
                                st.caption(f"Strength: {med.get('strength','—')}")
                            with c3:
                                st.caption(f"Dosage: {med.get('dosage','—')}")
                            with c4:
                                st.caption(f"Frequency: {med.get('frequency','—')}")
                            if med.get("notes"):
                                st.caption(f"📝 {med['notes']}")
                else:
                    st.info("No medicines extracted. Image quality may be low.")

                with st.expander("🔤 Raw OCR Text"):
                    st.text(ocr_text[:2000] if ocr_text else "No text extracted")

                ai_disclaimer(lang)
                st.info("⚕️ Always verify extracted medicines with your doctor or pharmacist before taking.")

    with tab_history:
        try:
            rows = execute_query(
                """SELECT p.id, p.original_filename, p.ocr_confidence, p.notes, p.created_at
                   FROM prescriptions p WHERE p.patient_id=:pid
                   ORDER BY p.created_at DESC""",
                {"pid": pid},
            )
        except Exception as e:
            st.error(f"Could not load prescriptions: {e}")
            return

        if not rows:
            st.info("No prescriptions uploaded yet.")
            return

        for row in rows:
            rx_id, fname, conf, notes, created = row
            with st.expander(f"📋 {fname or 'Prescription'} — {fmt_date(created)}"):
                if conf:
                    st.caption(f"OCR confidence: {conf*100:.0f}%")
                if notes:
                    st.write(notes)
                try:
                    items = execute_query(
                        "SELECT medicine_name, strength, dosage_instruction, frequency FROM prescription_items WHERE prescription_id=:rxid",
                        {"rxid": rx_id}
                    )
                    if items:
                        for item in items:
                            st.markdown(f"• **{item[0]}** {item[1] or ''} — {item[2] or ''} {item[3] or ''}")
                except Exception:
                    pass
