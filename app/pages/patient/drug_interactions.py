"""
Drug Interactions Checker
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.utils import section_header, ai_disclaimer
from app.services.ai.drug_interactions import check_interactions, get_interaction_summary


def show():
    user = require_auth(["patient","doctor"])
    lang = user["language"]

    section_header("⚗️ Drug Interaction Checker", "Check safety of taking multiple medicines together")
    ai_disclaimer(lang)

    st.info(
        "Enter the medicines you are currently taking (or planning to take). "
        "The system will check for known interactions."
    )

    with st.form("interaction_form"):
        meds_input = st.text_area(
            "Enter medicine names (one per line or comma-separated)",
            placeholder="Metformin\nAspirin\nWarfarin\nOmeprazole",
            height=150,
        )
        submitted = st.form_submit_button("🔍 Check Interactions", type="primary", use_container_width=True)

    if submitted:
        if not meds_input.strip():
            st.error("Please enter at least two medicine names.")
        else:
            import re
            medicines = [m.strip() for m in re.split(r"[,\n]+", meds_input) if m.strip()]
            if len(medicines) < 2:
                st.error("Please enter at least two medicines to check interactions.")
            else:
                with st.spinner(f"Checking {len(medicines)} medicines for interactions…"):
                    interactions = check_interactions(medicines)
                    summary = get_interaction_summary(interactions)

                # Summary row
                st.markdown("### 📊 Summary")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    color = "#EF4444" if summary["major"] > 0 else "#64748B"
                    st.markdown(f"<div style='color:{color};font-size:1.4rem;font-weight:700'>{summary['major']}</div><div style='color:#94A3B8'>Major</div>", unsafe_allow_html=True)
                with c2:
                    color = "#F59E0B" if summary["moderate"] > 0 else "#64748B"
                    st.markdown(f"<div style='color:{color};font-size:1.4rem;font-weight:700'>{summary['moderate']}</div><div style='color:#94A3B8'>Moderate</div>", unsafe_allow_html=True)
                with c3:
                    st.markdown(f"<div style='color:#10B981;font-size:1.4rem;font-weight:700'>{summary['minor']}</div><div style='color:#94A3B8'>Minor</div>", unsafe_allow_html=True)
                with c4:
                    st.markdown(f"<div style='color:#10B981;font-size:1.4rem;font-weight:700'>{summary['none']}</div><div style='color:#94A3B8'>No interaction</div>", unsafe_allow_html=True)

                if summary["major"] > 0:
                    st.error("⚠️ One or more **major interactions** found. Consult your doctor before taking these together.")
                elif summary["moderate"] > 0:
                    st.warning("⚠️ Moderate interactions found. Discuss with your doctor or pharmacist.")
                else:
                    st.success("✅ No major interactions found in our database.")

                st.markdown("### 🔍 Detailed Results")
                for interaction in interactions:
                    sev = interaction.get("severity","no interaction")
                    border_color = {"major":"#EF4444","moderate":"#F59E0B","minor":"#10B981"}.get(sev,"#334155")

                    st.markdown(
                        f"""<div style='border-left:4px solid {border_color};
                                        background:#1E293B; border-radius:8px;
                                        padding:12px 16px; margin-bottom:10px;'>
                            <strong>{interaction["drug_a"]}</strong> + <strong>{interaction["drug_b"]}</strong>
                            &nbsp; {interaction["severity_label"]}
                        </div>""",
                        unsafe_allow_html=True,
                    )
                    if interaction.get("found"):
                        with st.expander("📋 Details"):
                            st.markdown(f"**Effect:** {interaction.get('effect','')}")
                            st.markdown(f"**Recommended Action:** {interaction.get('action','')}")

                ai_disclaimer(lang)
                st.info(
                    "💡 This database contains common interactions. Always consult your doctor "
                    "or pharmacist for a complete medication review."
                )
