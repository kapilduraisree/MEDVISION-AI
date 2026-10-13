"""
Admin – Medicine Database Management
Add, edit, and manage the verified medicine database.
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.database import execute_query, execute_write
from app.core.utils import section_header, fmt_date


def show():
    user = require_auth(["admin"])
    section_header("💊 Medicine Database", "Manage the verified medicine reference database")

    tab_list, tab_add = st.tabs(["📋 Medicine List", "➕ Add Medicine"])

    with tab_list:
        search = st.text_input("🔍 Search medicines", placeholder="Brand name or generic name…")
        try:
            if search:
                rows = execute_query(
                    """SELECT id, brand_name, generic_name, drug_category,
                              is_otc, requires_prescription, is_verified, created_at
                       FROM medicines
                       WHERE LOWER(brand_name) LIKE :q OR LOWER(generic_name) LIKE :q
                       ORDER BY brand_name LIMIT 50""",
                    {"q": f"%{search.lower()}%"},
                )
            else:
                rows = execute_query(
                    """SELECT id, brand_name, generic_name, drug_category,
                              is_otc, requires_prescription, is_verified, created_at
                       FROM medicines ORDER BY brand_name LIMIT 100""",
                    {},
                )
        except Exception as e:
            st.error(str(e))
            return

        st.caption(f"{len(rows)} medicine(s) shown")

        for row in rows:
            mid, brand, generic, category, is_otc, req_rx, is_verified, created = row
            verified_icon = "✅" if is_verified else "⏳"
            otc_label = "OTC" if is_otc else "Rx"

            with st.expander(f"{verified_icon} **{brand}** ({generic or '—'}) — {category or '—'} — {otc_label}"):
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1:
                    st.caption(f"Category: {category or '—'}")
                    st.caption(f"OTC: {'Yes' if is_otc else 'No'}")
                with c2:
                    st.caption(f"Prescription required: {'Yes' if req_rx else 'No'}")
                    st.caption(f"Added: {fmt_date(created)}")
                with c3:
                    if not is_verified:
                        if st.button("✅ Verify", key=f"vmed_{mid}"):
                            try:
                                execute_write(
                                    "UPDATE medicines SET is_verified=TRUE WHERE id=:mid",
                                    {"mid": mid},
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))
                    if st.button("🗑️ Delete", key=f"dmed_{mid}"):
                        try:
                            execute_write("DELETE FROM medicines WHERE id=:mid", {"mid": mid})
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

    with tab_add:
        st.markdown("#### ➕ Add New Medicine")
        with st.form("add_medicine_form"):
            c1, c2 = st.columns(2)
            with c1:
                brand_name = st.text_input("Brand Name *", placeholder="e.g. Glycomet")
                generic_name = st.text_input("Generic Name", placeholder="e.g. Metformin HCl")
                active_ingredient = st.text_input("Active Ingredient")
                drug_category = st.text_input("Drug Category", placeholder="e.g. Antidiabetic")
                drug_class = st.text_input("Drug Class", placeholder="e.g. Biguanide")
            with c2:
                manufacturer = st.text_input("Manufacturer")
                is_otc = st.checkbox("Available Over the Counter (OTC)")
                is_controlled = st.checkbox("Controlled Substance")
                req_prescription = st.checkbox("Requires Prescription", value=True)
                is_verified = st.checkbox("Mark as Verified", value=True)

            general_purpose = st.text_area("General Purpose / Uses", height=80)
            common_precautions = st.text_area("Common Precautions", height=80)
            common_side_effects = st.text_area("Common Side Effects", height=80)
            storage_info = st.text_input("Storage Information", placeholder="Store below 25°C…")
            important_warnings = st.text_area("Important Warnings", height=60)

            submitted = st.form_submit_button("💾 Add Medicine", type="primary", use_container_width=True)

        if submitted:
            if not brand_name.strip():
                st.error("Brand name is required.")
            else:
                try:
                    execute_write(
                        """INSERT INTO medicines
                           (brand_name, generic_name, active_ingredient, drug_category,
                            drug_class, manufacturer, general_purpose, common_precautions,
                            common_side_effects, storage_information, important_warnings,
                            is_otc, is_controlled, requires_prescription, is_verified,
                            source, created_at)
                           VALUES (:brand,:generic,:active,:category,:class,:mfr,
                                   :purpose,:precautions,:side_effects,:storage,:warnings,
                                   :otc,:controlled,:rx,:verified,
                                   'MedVision Admin',NOW())""",
                        {"brand": brand_name, "generic": generic_name,
                         "active": active_ingredient, "category": drug_category,
                         "class": drug_class, "mfr": manufacturer,
                         "purpose": general_purpose, "precautions": common_precautions,
                         "side_effects": common_side_effects, "storage": storage_info,
                         "warnings": important_warnings, "otc": is_otc,
                         "controlled": is_controlled, "rx": req_prescription,
                         "verified": is_verified},
                    )
                    st.success(f"✅ **{brand_name}** added to the medicine database.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to add medicine: {e}")
