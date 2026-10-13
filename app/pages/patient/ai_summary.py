"""
AI Health Summary - generates a multimodal summary combining all patient data.
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.database import execute_query
from app.core.utils import section_header, ai_disclaimer
from app.services.ai.health_summary import generate_health_summary


def show():
    user = require_auth(["patient"])
    pid = user["patient_id"]
    lang = user["language"]

    section_header("🤖 AI Health Summary", "A combined AI analysis of your health data")
    ai_disclaimer(lang)

    st.info(
        "The AI Health Summary combines your symptoms, recent lab results, medications, "
        "and health metrics to produce a plain-language overview. It is **not a diagnosis**."
    )

    # ── Gather patient data ───────────────────────────────────────────────────
    patient_data = {"symptoms": [], "medications": [], "reports": [], "metrics": [], "profile": {}}

    try:
        profile = execute_query(
            """SELECT p.date_of_birth, p.gender, p.blood_group,
                      p.chronic_conditions, p.known_allergies, p.current_medications
               FROM patients p WHERE p.id=:pid""",
            {"pid": pid},
        )
        if profile:
            r = profile[0]
            from datetime import date
            age = ""
            if r[0]:
                try:
                    age = str(date.today().year - r[0].year)
                except Exception:
                    age = ""
            patient_data["profile"] = {
                "age": age, "gender": r[1] or "",
                "blood_group": r[2] or "",
                "chronic_conditions": r[3] or "",
                "known_allergies": r[4] or "",
            }
            if r[5]:
                patient_data["medications"] = [m.strip() for m in r[5].split(",")]
    except Exception:
        pass

    try:
        symptoms = execute_query(
            "SELECT description FROM symptoms WHERE patient_id=:pid ORDER BY created_at DESC LIMIT 5",
            {"pid": pid},
        )
        patient_data["symptoms"] = [s[0] for s in symptoms if s[0]]
    except Exception:
        pass

    try:
        meds = execute_query(
            "SELECT medicine_name, strength FROM medication_schedules WHERE patient_id=:pid AND is_active=TRUE LIMIT 10",
            {"pid": pid},
        )
        if meds:
            patient_data["medications"] = [f"{m[0]} {m[1] or ''}".strip() for m in meds]
    except Exception:
        pass

    try:
        report_vals = execute_query(
            """SELECT rv.test_name, rv.result, rv.unit, rv.status
               FROM report_values rv
               JOIN medical_reports mr ON rv.report_id = mr.id
               WHERE mr.patient_id=:pid
               ORDER BY mr.created_at DESC LIMIT 20""",
            {"pid": pid},
        )
        patient_data["reports"] = [
            {"test_name": r[0], "result": r[1], "unit": r[2], "status": r[3]}
            for r in report_vals
        ]
    except Exception:
        pass

    try:
        metrics = execute_query(
            """SELECT metric_name, value, unit
               FROM health_metrics WHERE patient_id=:pid
               ORDER BY recorded_date DESC LIMIT 10""",
            {"pid": pid},
        )
        patient_data["metrics"] = [
            {"metric_name": m[0], "value": m[1], "unit": m[2]} for m in metrics
        ]
    except Exception:
        pass

    # ── Show data overview ────────────────────────────────────────────────────
    st.markdown("### 📊 Data Used for Summary")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Symptoms", len(patient_data["symptoms"]))
    with c2:
        st.metric("Medications", len(patient_data["medications"]))
    with c3:
        st.metric("Lab Values", len(patient_data["reports"]))
    with c4:
        st.metric("Health Metrics", len(patient_data["metrics"]))

    profile = patient_data["profile"]
    if profile.get("age") or profile.get("gender"):
        cols = st.columns(4)
        fields = [("Age", profile.get("age","—")), ("Gender", profile.get("gender","—")),
                  ("Blood Group", profile.get("blood_group","—")),
                  ("Conditions", profile.get("chronic_conditions","None")[:30])]
        for col, (label, val) in zip(cols, fields):
            with col:
                st.caption(f"**{label}:** {val}")

    st.markdown("---")

    if st.button("🤖 Generate AI Health Summary", type="primary", use_container_width=True):
        total_data = sum([
            len(patient_data["symptoms"]),
            len(patient_data["medications"]),
            len(patient_data["reports"]),
        ])
        if total_data == 0:
            st.warning(
                "Not enough data to generate a meaningful summary. "
                "Upload reports, log symptoms, or add medication reminders first."
            )
        else:
            with st.spinner("Generating AI health summary…"):
                summary = generate_health_summary(patient_data, lang)

            st.markdown("### 📋 Your AI Health Summary")
            st.markdown(summary)
            ai_disclaimer(lang)

            st.caption(
                "💡 Take this summary to your next doctor visit to discuss your overall health picture."
            )
