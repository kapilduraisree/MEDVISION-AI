"""
MedVision AI – Live Drug Lookup
Fetches real-time drug data from OpenFDA and RxNorm (no API key needed).
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.utils import section_header, ai_disclaimer
from app.services.ai.live_data import (
    enrich_drug_info, get_rxnorm_interactions,
    get_drug_recalls, search_drug_fda
)


def show():
    user = require_auth(["patient", "doctor", "admin"])
    lang = user["language"]

    section_header("🌐 Live Drug Information", "Real-time data from US FDA & NLM databases")
    ai_disclaimer(lang)

    st.info(
        "Data is fetched live from **OpenFDA** (US Food & Drug Administration) and "
        "**RxNorm** (National Library of Medicine). Results are cached for 30 minutes. "
        "Information reflects US drug labeling and may differ from Indian prescribing information.",
        icon="ℹ️",
    )

    tab_search, tab_interactions, tab_recalls = st.tabs([
        "🔍 Drug Label Search", "⚗️ Live Interaction Check", "⚠️ Recall Alerts"
    ])

    # ────────────────────────────────────────────────────────────────────────
    # TAB 1 – Drug Label Search
    # ────────────────────────────────────────────────────────────────────────
    with tab_search:
        st.markdown("#### Search US FDA Drug Labels")
        drug_query = st.text_input(
            "Enter drug name (brand or generic)",
            placeholder="e.g. Metformin, Paracetamol, Atorvastatin…",
            key="fda_search",
        )

        if drug_query and len(drug_query.strip()) >= 3:
            with st.spinner(f"Fetching live FDA data for **{drug_query}**…"):
                data = enrich_drug_info(drug_query.strip())

            if not data.get("found"):
                st.warning(
                    f"No FDA label found for **{drug_query}**. "
                    "Try the generic name, or check spelling."
                )
                if data.get("error"):
                    st.caption(f"API error: {data['error']}")
            else:
                # Header row
                st.success(f"✅ Found: **{drug_query}**  •  Source: {data.get('source','OpenFDA')}")

                brands = data.get("brand_names", [])
                generics = data.get("generic_names", [])
                drug_classes = data.get("drug_class", [])

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Brand names:** {', '.join(brands[:3]) if brands else '—'}")
                with col2:
                    st.markdown(f"**Generic:** {', '.join(generics[:2]) if generics else '—'}")
                with col3:
                    st.markdown(f"**Manufacturer:** {data.get('manufacturer') or '—'}")

                if drug_classes:
                    st.markdown(f"**Drug class:** {', '.join(drug_classes[:3])}")

                st.markdown("---")

                # Adverse event stats
                total_ev  = data.get("adverse_event_total", 0)
                serious_ev = data.get("adverse_event_serious", 0)
                if total_ev:
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        st.metric("📊 FDA Adverse Event Reports (FAERS)", f"{total_ev:,}")
                    with ec2:
                        pct = (serious_ev / total_ev * 100) if total_ev else 0
                        st.metric("🔴 Serious Reports", f"{serious_ev:,}", f"{pct:.1f}% of total")
                    st.caption("FAERS reports are submitted voluntarily; they do not prove causation.")

                st.markdown("---")

                # Detailed sections
                _section_block("🎯 Indications & Usage",       data.get("indications"))
                _section_block("💊 Dosage & Administration",   data.get("dosage"))
                _section_block("⚠️ Warnings",                  data.get("warnings"), warning=True)
                _section_block("🚫 Contraindications",         data.get("contraindications"), warning=True)
                _section_block("😣 Adverse Reactions",         data.get("adverse_reactions"))
                _section_block("⚗️ Drug Interactions",         data.get("drug_interactions_text"))
                _section_block("🤰 Pregnancy",                 data.get("pregnancy_category"))
                _section_block("🌡️ Storage & Handling",        data.get("storage"))

                ai_disclaimer(lang)
                st.caption("Source: OpenFDA (api.fda.gov) — US FDA drug label database.")

    # ────────────────────────────────────────────────────────────────────────
    # TAB 2 – Live Interaction Check (RxNorm)
    # ────────────────────────────────────────────────────────────────────────
    with tab_interactions:
        st.markdown("#### Live Drug Interaction Check via RxNorm")
        st.info(
            "This uses the **NLM RxNorm Interaction API** — a live US government drug "
            "interaction database. Results may differ from Indian/local databases.",
            icon="🔬",
        )

        with st.form("rxnorm_form"):
            meds_input = st.text_area(
                "Enter medicine names (one per line or comma-separated)",
                placeholder="Warfarin\nAspirin\nOmeprazole",
                height=120,
            )
            submitted = st.form_submit_button(
                "🔍 Check Live Interactions", type="primary", use_container_width=True
            )

        if submitted:
            import re
            medicines = [m.strip() for m in re.split(r"[,\n]+", meds_input) if m.strip()]
            if len(medicines) < 2:
                st.error("Enter at least two medicine names.")
            else:
                with st.spinner(f"Querying RxNorm for {len(medicines)} medicines…"):
                    interactions = get_rxnorm_interactions(medicines)

                if not interactions:
                    st.success(
                        f"✅ RxNorm found **no known interactions** between: "
                        f"{', '.join(medicines)}\n\n"
                        "Note: Absence of a result does not guarantee safety. "
                        "Always confirm with your pharmacist or doctor."
                    )
                else:
                    # Group by severity
                    high     = [i for i in interactions if "high"    in i.get("severity","").lower()]
                    moderate = [i for i in interactions if "medium"  in i.get("severity","").lower()
                                or "moderate" in i.get("severity","").lower()]
                    low      = [i for i in interactions if "low"     in i.get("severity","").lower()]
                    other    = [i for i in interactions if i not in high + moderate + low]

                    # Summary bar
                    sc1, sc2, sc3 = st.columns(3)
                    with sc1:
                        clr = "#EF4444" if high else "#64748B"
                        st.markdown(f"<div style='color:{clr};font-size:1.5rem;font-weight:700'>{len(high)}</div>"
                                    "<div style='color:#94A3B8'>High severity</div>", unsafe_allow_html=True)
                    with sc2:
                        clr = "#F59E0B" if moderate else "#64748B"
                        st.markdown(f"<div style='color:{clr};font-size:1.5rem;font-weight:700'>{len(moderate)}</div>"
                                    "<div style='color:#94A3B8'>Moderate</div>", unsafe_allow_html=True)
                    with sc3:
                        st.markdown(f"<div style='color:#10B981;font-size:1.5rem;font-weight:700'>{len(low)+len(other)}</div>"
                                    "<div style='color:#94A3B8'>Low / other</div>", unsafe_allow_html=True)

                    if high:
                        st.error(f"⚠️ **{len(high)} high-severity interaction(s) found.** Consult your doctor before taking these together.")
                    elif moderate:
                        st.warning(f"⚠️ **{len(moderate)} moderate interaction(s) found.** Discuss with your doctor or pharmacist.")
                    else:
                        st.success("No high-severity interactions found.")

                    st.markdown("### Detailed Results")
                    for ixn in interactions:
                        sev   = ixn.get("severity", "unknown").lower()
                        label = ixn.get("severity_label", f"• {sev.capitalize()}")
                        border = {"high":"#EF4444","medium":"#F59E0B","moderate":"#F59E0B","low":"#10B981"}.get(sev,"#334155")

                        st.markdown(
                            f"<div style='border-left:4px solid {border};background:#1E293B;"
                            f"border-radius:8px;padding:12px 16px;margin-bottom:10px;'>"
                            f"<strong>{ixn.get('drug_a','')}</strong> + "
                            f"<strong>{ixn.get('drug_b','')}</strong> &nbsp; {label}"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
                        if ixn.get("description"):
                            with st.expander("📋 Description"):
                                st.markdown(ixn["description"])
                                st.caption(f"Source: {ixn.get('source','RxNorm')}")

                    ai_disclaimer(lang)
                    st.caption("Source: RxNorm Interaction API (rxnav.nlm.nih.gov) — NLM/NIH.")

    # ────────────────────────────────────────────────────────────────────────
    # TAB 3 – FDA Recall Alerts
    # ────────────────────────────────────────────────────────────────────────
    with tab_recalls:
        st.markdown("#### FDA Drug Recall Alerts")
        st.warning(
            "⚠️ These are **US FDA recalls** and may not apply to medicines sold in India. "
            "Contact your pharmacist or the CDSCO (India) for local recall information.",
            icon="⚠️",
        )

        recall_drug = st.text_input(
            "Search for recall records",
            placeholder="e.g. Metformin, Ranitidine, Valsartan…",
            key="recall_search",
        )

        if recall_drug and len(recall_drug.strip()) >= 3:
            with st.spinner(f"Searching FDA recall database for **{recall_drug}**…"):
                recalls = get_drug_recalls(recall_drug.strip(), limit=10)

            if not recalls:
                st.success(f"✅ No FDA recall records found for **{recall_drug}**.")
                st.caption("This covers US FDA enforcement actions only.")
            else:
                st.error(f"⚠️ Found **{len(recalls)}** recall record(s) for **{recall_drug}**.")
                for rec in recalls:
                    cls = rec.get("classification","")
                    cls_color = {"Class I":"#EF4444","Class II":"#F59E0B","Class III":"#10B981"}.get(cls,"#64748B")

                    with st.expander(
                        f"🚨 {rec.get('date','')}  •  {rec.get('recalling_firm','')}  •  "
                        f"**{cls}**"
                    ):
                        st.markdown(f"**Product:** {rec.get('product','')}")
                        st.markdown(
                            f"**Classification:** "
                            f"<span style='color:{cls_color};font-weight:600'>{cls}</span>",
                            unsafe_allow_html=True,
                        )
                        st.markdown(f"**Recall Number:** {rec.get('recall_number','—')}")
                        st.markdown(f"**Status:** {rec.get('status','—')}")
                        if rec.get("reason"):
                            st.markdown(f"**Reason:** {rec['reason']}")
                        st.caption(f"Source: {rec.get('source','FDA')}")

                ai_disclaimer(lang)
                st.caption("Source: OpenFDA Enforcement Database (api.fda.gov/drug/enforcement.json)")

        # Recall classification legend
        with st.expander("ℹ️ What do recall classifications mean?"):
            st.markdown("""
| Class | Meaning |
|-------|---------|
| **Class I** | 🔴 Most serious — reasonable probability of serious adverse health consequences or death |
| **Class II** | 🟡 May cause temporary or medically reversible adverse health consequences |
| **Class III** | 🟢 Unlikely to cause adverse health consequences but violates FDA regulations |
            """)


# ── Helper ────────────────────────────────────────────────────────────────────
def _section_block(title: str, content: str, warning: bool = False):
    """Render one labelled expandable section, only if content is non-empty."""
    if not content or not content.strip():
        return
    with st.expander(title):
        if warning:
            st.warning(content[:1000])
        else:
            st.markdown(content[:1000])
        if len(content) > 1000:
            st.caption("(truncated — see full FDA label for complete information)")
