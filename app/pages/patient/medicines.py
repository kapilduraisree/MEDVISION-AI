"""
Medicine Search & Scanner - search medicine database and scan strips.
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.database import execute_query
from app.core.utils import section_header, ai_disclaimer
from app.services.ai.medicine_scanner import scan_medicine_strip, check_expiry_status


def show():
    user = require_auth(["patient","doctor","admin"])
    lang = user["language"]

    section_header("💊 Medicine Information", "Search medicines and scan strip packaging")

    tab_search, tab_scan = st.tabs(["🔍 Search Medicines", "📷 Scan Medicine Strip"])

    # ── Search tab ────────────────────────────────────────────────────────────
    with tab_search:
        query = st.text_input("Search by brand name or generic name", placeholder="e.g. Metformin, Paracetamol…")

        if query and len(query) >= 2:
            try:
                results = execute_query(
                    """SELECT brand_name, generic_name, drug_category, general_purpose,
                              common_precautions, common_side_effects, storage_information,
                              important_warnings, is_otc, requires_prescription
                       FROM medicines
                       WHERE LOWER(brand_name) LIKE :q OR LOWER(generic_name) LIKE :q
                       LIMIT 10""",
                    {"q": f"%{query.lower()}%"},
                )
            except Exception as e:
                st.error(f"Search failed: {e}")
                results = []

            if results:
                st.success(f"Found {len(results)} result(s)")
                for row in results:
                    (brand, generic, category, purpose, precautions,
                     side_effects, storage, warnings, is_otc, req_rx) = row
                    with st.expander(f"💊 {brand}  —  {generic or ''}"):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown(f"**Category:** {category or '—'}")
                            st.markdown(f"**OTC:** {'Yes' if is_otc else 'No'}  |  **Prescription Required:** {'Yes' if req_rx else 'No'}")
                        with c2:
                            pass
                        if purpose:
                            st.markdown(f"**General Purpose:** {purpose}")
                        if precautions:
                            st.markdown(f"**Precautions:** {precautions}")
                        if side_effects:
                            st.markdown(f"**Common Side Effects:** {side_effects}")
                        if storage:
                            st.markdown(f"**Storage:** {storage}")
                        if warnings:
                            st.warning(f"⚠️ {warnings}")
                        ai_disclaimer(lang)
            elif query:
                st.info("No medicines found. Try a different search term.")
                st.caption("Our medicine database grows over time. Ask your pharmacist for complete information.")

        elif not query:
            try:
                total = execute_query("SELECT COUNT(*) FROM medicines", {})
                count = total[0][0] if total else 0
                st.info(f"📦 Medicine database contains **{count}** verified entries. Start typing to search.")
            except Exception:
                st.info("Start typing a medicine name to search.")

    # ── Scan tab ──────────────────────────────────────────────────────────────
    with tab_scan:
        st.markdown("#### 📷 Scan Medicine Packaging")
        st.info("Upload a clear photo of the medicine strip/box to extract expiry date, batch number, and MRP.")

        with st.form("scan_form"):
            uploaded = st.file_uploader(
                "Upload medicine strip or packaging image",
                type=["jpg","jpeg","png","bmp"],
            )
            submitted = st.form_submit_button("🔍 Scan Packaging", type="primary", use_container_width=True)

        if submitted:
            if not uploaded:
                st.error("Please upload an image.")
            else:
                with st.spinner("Scanning packaging…"):
                    file_bytes = uploaded.read()
                    result = scan_medicine_strip(file_bytes=file_bytes, filename=uploaded.name)

                if result.get("is_mock"):
                    st.warning("⚠️ Could not read real data — showing demo result.")

                st.success("✅ Scan complete")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("Medicine", result.get("medicine_name","—")[:25] if result.get("medicine_name") else "—")
                with c2:
                    expiry = result.get("expiry_date","—")
                    st.metric("Expiry", expiry or "—")
                with c3:
                    st.metric("Batch No", result.get("batch_no","—") or "—")
                with c4:
                    st.metric("MRP", result.get("mrp","—") or "—")

                # Expiry status
                expiry_status = check_expiry_status(result.get("expiry_date",""))
                if expiry_status["status"] == "expired":
                    st.error(expiry_status["message"])
                elif expiry_status["status"] == "expiring_soon":
                    st.warning(expiry_status["message"])
                elif expiry_status["status"] == "valid":
                    st.success(expiry_status["message"])

                with st.expander("🔤 Raw OCR Text"):
                    st.text(result.get("raw_text","")[:1000])
                ai_disclaimer(lang)
