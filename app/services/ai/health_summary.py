"""
MedVision AI – Health Summary Service (v2)
Uses the unified LLM client (Gemini → OpenAI → Ollama → rule-based).
generate_health_summary() signature unchanged for backward compatibility.
"""
from app.core.config import settings

SYSTEM_PROMPT = """You are a medical information assistant helping a patient understand their health data.

STRICT RULES:
1. Never diagnose diseases or conditions.
2. Never recommend, prescribe, or advise changing medications.
3. Summarise factually from the data provided — do not invent values.
4. Use plain, patient-friendly language (avoid jargon).
5. Highlight values outside normal range clearly but without alarming language.
6. End with: "⚠️ This summary is for informational purposes only. Please consult your doctor."
"""


def generate_health_summary(patient_data: dict, language: str = "en") -> str:
    """
    Generate a plain-language health summary.
    patient_data keys: symptoms, reports, medications, metrics, profile
    """
    lang = language if language in ("en", "ta") else "en"
    prompt = _build_prompt(patient_data, lang)

    try:
        from app.services.ai.llm_client import llm_complete
        system = SYSTEM_PROMPT + ("\nRespond in Tamil (தமிழ்).\n" if lang == "ta" else "")
        result = llm_complete(prompt, system=system, max_tokens=700, temperature=0.35)
        disclaimer = settings.AI_DISCLAIMER_TA if lang == "ta" else settings.AI_DISCLAIMER_EN
        return result + f"\n\n{disclaimer}"
    except RuntimeError:
        pass  # No LLM — use rule-based
    except Exception:
        pass

    return _rule_based_summary(patient_data, lang)


def _build_prompt(data: dict, language: str) -> str:
    lines = ["Please generate a health summary for this patient based on the following data:\n"]

    p = data.get("profile", {})
    if p:
        lines.append(f"Patient: Age {p.get('age','N/A')}, Gender: {p.get('gender','N/A')}, "
                     f"Blood group: {p.get('blood_group','N/A')}")
        if p.get("chronic_conditions"):
            lines.append(f"Known conditions: {p['chronic_conditions']}")
        if p.get("known_allergies"):
            lines.append(f"Allergies: {p['known_allergies']}")

    if data.get("symptoms"):
        lines.append(f"\nRecent symptoms: {'; '.join(data['symptoms'][:5])}")

    if data.get("medications"):
        lines.append(f"\nActive medications: {', '.join(data['medications'][:10])}")

    reports = data.get("reports", [])
    abnormal = [r for r in reports if r.get("status") in ("attention", "abnormal")]
    normal_count = sum(1 for r in reports if r.get("status") == "normal")
    if reports:
        lines.append(f"\nLab results: {len(reports)} values total, {normal_count} normal.")
        if abnormal:
            lines.append("Values outside normal range:")
            for r in abnormal[:8]:
                lines.append(f"  - {r.get('test_name')}: {r.get('result')} {r.get('unit','')} "
                             f"(ref: {r.get('reference_range_text','N/A')}) — {r.get('status')}")

    if data.get("metrics"):
        lines.append("\nRecent health metrics:")
        for m in data["metrics"][:6]:
            lines.append(f"  - {m.get('metric_name')}: {m.get('value')} {m.get('unit','')}")

    if language == "ta":
        lines.append("\nPlease write the summary in Tamil.")

    return "\n".join(lines)


def _rule_based_summary(data: dict, language: str) -> str:
    disclaimer = settings.AI_DISCLAIMER_TA if language == "ta" else settings.AI_DISCLAIMER_EN

    if language == "ta":
        parts = ["**உங்கள் சுகாதார சுருக்கம்**\n"]
        p = data.get("profile", {})
        if p.get("chronic_conditions"):
            parts.append(f"🏥 **அறியப்பட்ட நிலைகள்:** {p['chronic_conditions']}")
        if data.get("symptoms"):
            parts.append(f"📋 **சமீபத்திய அறிகுறிகள்:** {', '.join(data['symptoms'][:5])}")
        if data.get("medications"):
            parts.append(f"💊 **தற்போதைய மருந்துகள்:** {', '.join(data['medications'][:8])}")
        reports = data.get("reports", [])
        abnormal = [r for r in reports if r.get("status") in ("attention","abnormal")]
        normal = [r for r in reports if r.get("status") == "normal"]
        if normal:
            parts.append(f"✅ **{len(normal)} பரிசோதனைகள்** சாதாரண வரம்பில் உள்ளன.")
        if abnormal:
            parts.append("⚠️ **கவனம் தேவை:** " + ", ".join(r.get("test_name","") for r in abnormal[:5]))
        parts.append(f"\n{disclaimer}")
        return "\n\n".join(parts)

    parts = ["**Your Health Summary**\n"]
    p = data.get("profile", {})
    if p.get("chronic_conditions"):
        parts.append(f"🏥 **Known conditions:** {p['chronic_conditions']}")
    if p.get("known_allergies"):
        parts.append(f"🚨 **Allergies:** {p['known_allergies']}")
    if data.get("symptoms"):
        parts.append(f"📋 **Recent symptoms:** {', '.join(data['symptoms'][:5])}")
    if data.get("medications"):
        parts.append(f"💊 **Active medications:** {', '.join(data['medications'][:8])}")
    reports = data.get("reports", [])
    normal = [r for r in reports if r.get("status") == "normal"]
    attention = [r for r in reports if r.get("status") == "attention"]
    abnormal = [r for r in reports if r.get("status") == "abnormal"]
    if normal:
        parts.append(f"✅ **{len(normal)} lab values** within normal range.")
    if attention:
        parts.append("🟡 **Needs attention:** " + ", ".join(r.get("test_name","") for r in attention[:5]))
    if abnormal:
        parts.append("🔴 **Outside normal range:** " + ", ".join(r.get("test_name","") for r in abnormal[:5]))
    if data.get("metrics"):
        for m in data["metrics"][:4]:
            parts.append(f"📊 {m.get('metric_name')}: **{m.get('value')} {m.get('unit','')}**")
    if not any([data.get("symptoms"), abnormal, attention]):
        parts.append("Overall your recorded data does not show immediate concerns. Keep up regular check-ups.")
    parts.append(f"\n{disclaimer}")
    return "\n\n".join(parts)
