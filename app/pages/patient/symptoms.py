"""
Symptoms Tracker - log symptoms via text, get emergency screening.
"""
import streamlit as st
from datetime import datetime
from app.core.auth import require_auth
from app.core.database import execute_query, execute_write
from app.core.utils import section_header, fmt_datetime, ai_disclaimer
from app.services.ai.chatbot_service import is_emergency, EMERGENCY_RESPONSE_EN, EMERGENCY_RESPONSE_TA

EMERGENCY_SYMPTOMS = [
    "chest pain","heart attack","can't breathe","cannot breathe","difficulty breathing",
    "severe bleeding","unconscious","stroke","paralysis","seizure","overdose","poisoning",
]


def show():
    user = require_auth(["patient"])
    pid = user["patient_id"]
    lang = user["language"]

    section_header("🩺 Symptom Tracker", "Log your symptoms and get immediate guidance")
    ai_disclaimer(lang)

    tab_log, tab_history = st.tabs(["📝 Log Symptoms", "📋 History"])

    with tab_log:
        st.markdown("#### Describe your symptoms")
        with st.form("symptom_form"):
            description = st.text_area(
                "What symptoms are you experiencing?",
                placeholder="e.g. Headache for 2 days, mild fever, fatigue…",
                height=120,
            )
            col1, col2, col3 = st.columns(3)
            with col1:
                severity = st.selectbox("Severity", ["mild","moderate","severe"])
            with col2:
                duration = st.text_input("Duration", placeholder="e.g. 2 days, 3 hours")
            with col3:
                location = st.text_input("Body area (optional)", placeholder="e.g. chest, head")

            submitted = st.form_submit_button("🔍 Analyse Symptoms", type="primary", use_container_width=True)

        if submitted:
            if not description.strip():
                st.error("Please describe your symptoms.")
            else:
                is_em = is_emergency(description)
                try:
                    execute_write(
                        """INSERT INTO symptoms
                           (patient_id, description, duration, severity,
                            location_on_body, language, is_emergency_flagged, created_at)
                           VALUES (:pid,:desc,:dur,:sev,:loc,:lang,:em,NOW())""",
                        {"pid": pid, "desc": description, "dur": duration,
                         "sev": severity, "loc": location, "lang": lang, "em": is_em},
                    )
                except Exception as e:
                    st.warning(f"Symptom saved locally but DB error: {e}")

                if is_em:
                    st.error("🚨 **EMERGENCY DETECTED**")
                    resp = EMERGENCY_RESPONSE_TA if lang == "ta" else EMERGENCY_RESPONSE_EN
                    st.markdown(resp)
                else:
                    st.success("✅ Symptoms logged successfully.")
                    _show_symptom_guidance(description, severity, lang)

    with tab_history:
        try:
            rows = execute_query(
                """SELECT description, severity, duration, location_on_body,
                          is_emergency_flagged, created_at
                   FROM symptoms WHERE patient_id=:pid
                   ORDER BY created_at DESC LIMIT 20""",
                {"pid": pid},
            )
        except Exception as e:
            st.error(f"Could not load history: {e}")
            return

        if not rows:
            st.info("No symptoms logged yet.")
            return

        for row in rows:
            desc, sev, dur, loc, is_em, created = row
            icon = "🚨" if is_em else "🟡" if sev == "severe" else "🟢"
            with st.expander(f"{icon} {fmt_datetime(created)} — {sev.capitalize() if sev else 'N/A'} severity"):
                st.write(desc)
                if dur:
                    st.caption(f"Duration: {dur}")
                if loc:
                    st.caption(f"Location: {loc}")
                if is_em:
                    st.error("⚠️ This was flagged as a potential emergency.")


def _show_symptom_guidance(description: str, severity: str, lang: str):
    st.markdown("#### 💡 General Guidance")
    if severity == "severe":
        st.warning(
            "Your symptoms are marked as **severe**. Please consult a doctor as soon as possible. "
            "If you feel it is an emergency, call **112** immediately."
        )
    elif severity == "moderate":
        st.info(
            "Your symptoms are moderate. Monitor them closely. If they worsen or persist "
            "more than 2-3 days, consult a healthcare provider."
        )
    else:
        st.info(
            "Your symptoms appear mild. Rest, stay hydrated, and monitor for changes. "
            "Consult a doctor if symptoms persist or worsen."
        )
    ai_disclaimer(lang)
    st.caption("Tip: Bring this symptom log to your next doctor visit for reference.")
