"""
Health Summary Generator – combines multimodal inputs into a structured summary.
"""

DISCLAIMER_EN = (
    "\n\n---\n"
    "⚠️ IMPORTANT DISCLAIMER: This summary is AI-generated for informational purposes only. "
    "It is NOT a medical diagnosis or treatment recommendation. "
    "All information must be reviewed by a qualified healthcare professional before any clinical decision."
)

DISCLAIMER_TA = (
    "\n\n---\n"
    "⚠️ முக்கிய அறிவிப்பு: இந்த சுருக்கம் AI-ஆல் உருவாக்கப்பட்டது மற்றும் "
    "தகவல் நோக்கங்களுக்காக மட்டுமே. இது மருத்துவ நோயறிதல் அல்ல. "
    "எந்த மருத்துவ முடிவுக்கும் முன் தகுதி வாய்ந்த மருத்துவரால் இது மதிப்பாய்வு செய்யப்பட வேண்டும்."
)


def generate_health_summary(
    patient_name: str,
    symptoms: list,
    report_values: list,
    medications: list,
    previous_reports: list,
    language: str = "en",
) -> dict:
    """
    Generate a structured multimodal health summary.
    Returns a dict with sections.
    """
    lang = language if language in ["en", "ta"] else "en"

    sections = {}

    # 1. Patient-reported symptoms
    sections["symptoms"] = _build_symptom_section(symptoms, lang)

    # 2. Extracted report findings
    sections["report_findings"] = _build_report_section(report_values, lang)

    # 3. Current medications
    sections["medications"] = _build_medication_section(medications, lang)

    # 4. Important warnings
    sections["warnings"] = _build_warnings_section(report_values, medications, lang)

    # 5. Historical changes
    sections["historical_changes"] = _build_historical_section(previous_reports, report_values, lang)

    # 6. Questions for doctor
    sections["questions_for_doctor"] = _build_doctor_questions(
        report_values, symptoms, medications, lang
    )

    # 7. Recommended follow-up
    sections["recommended_followup"] = _build_followup_section(report_values, lang)

    disclaimer = DISCLAIMER_TA if lang == "ta" else DISCLAIMER_EN

    full_text = _compile_full_text(patient_name, sections, lang, disclaimer)

    return {
        "sections": sections,
        "full_text": full_text,
        "language": lang,
        "disclaimer": disclaimer.strip(),
        "is_ai_generated": True,
    }


def _build_symptom_section(symptoms: list, lang: str) -> str:
    if not symptoms:
        return "No symptoms reported." if lang == "en" else "எந்த அறிகுறியும் பதிவு செய்யப்படவில்லை."

    if lang == "ta":
        lines = ["**நோயாளி பதிவிட்ட அறிகுறிகள்:**"]
        for s in symptoms:
            lines.append(f"• {s.get('description', '')} "
                         f"(தீவிரம்: {s.get('severity', 'குறிப்பிடப்படவில்லை')})")
    else:
        lines = ["**Patient-Reported Symptoms:**"]
        for s in symptoms:
            lines.append(f"• {s.get('description', '')} "
                         f"(Severity: {s.get('severity', 'not specified')})")

    return "\n".join(lines)


def _build_report_section(report_values: list, lang: str) -> str:
    if not report_values:
        return "No recent report values available." if lang == "en" else "சமீபத்திய அறிக்கை மதிப்புகள் இல்லை."

    abnormal = [v for v in report_values if v.get("status") in ("attention", "abnormal")]
    normal = [v for v in report_values if v.get("status") == "normal"]

    if lang == "ta":
        lines = ["**கண்டுபிடிப்புகள் (சமீபத்திய அறிக்கையிலிருந்து):**"]
        if abnormal:
            lines.append("கவனம் தேவைப்படும் மதிப்புகள்:")
            for v in abnormal:
                lines.append(f"  • {v.get('test_name')}: {v.get('result')} {v.get('unit')} "
                              f"(நிலை: {v.get('status')})")
        lines.append(f"\n{len(normal)} மதிப்புகள் சாதாரண வரம்பில் உள்ளன.")
    else:
        lines = ["**Report Findings (Most Recent):**"]
        if abnormal:
            lines.append("Values requiring attention:")
            for v in abnormal:
                lines.append(f"  • {v.get('test_name')}: {v.get('result')} {v.get('unit')} "
                              f"(Status: {v.get('status')})")
        lines.append(f"\n{len(normal)} values are within normal range.")

    return "\n".join(lines)


def _build_medication_section(medications: list, lang: str) -> str:
    if not medications:
        return "No current medications recorded." if lang == "en" else "தற்போதைய மருந்துகள் பதிவு செய்யப்படவில்லை."

    if lang == "ta":
        lines = ["**தற்போதைய மருந்துகள்:**"]
        for m in medications:
            lines.append(f"• {m.get('medicine_name')} {m.get('strength', '')} - "
                         f"{m.get('frequency', '')} {m.get('duration', '')}")
    else:
        lines = ["**Current Medications:**"]
        for m in medications:
            lines.append(f"• {m.get('medicine_name')} {m.get('strength', '')} - "
                         f"{m.get('frequency', '')} {m.get('duration', '')}")

    return "\n".join(lines)


def _build_warnings_section(report_values: list, medications: list, lang: str) -> str:
    warnings = []

    abnormal = [v for v in report_values if v.get("status") == "abnormal"]
    if abnormal:
        if lang == "ta":
            for v in abnormal:
                warnings.append(f"⚠️ {v.get('test_name')} அசாதாரண வரம்பில் உள்ளது.")
        else:
            for v in abnormal:
                warnings.append(f"⚠️ {v.get('test_name')} is outside normal range.")

    if not warnings:
        return ("No major documented warnings at this time." if lang == "en"
                else "இப்போது முக்கிய எச்சரிக்கைகள் எதுவும் இல்லை.")

    return "\n".join(warnings)


def _build_historical_section(prev_reports: list, current_values: list, lang: str) -> str:
    if not prev_reports:
        return ("No previous reports available for comparison." if lang == "en"
                else "ஒப்பீட்டிற்கு முந்தைய அறிக்கைகள் இல்லை.")

    if lang == "ta":
        return f"{len(prev_reports)} முந்தைய அறிக்கைகள் பதிவு செய்யப்பட்டுள்ளன. உங்கள் மருத்துவர் இவற்றை ஒப்பிட்டு மதிப்பீடு செய்வார்."
    else:
        return (f"{len(prev_reports)} previous report(s) are recorded. "
                "Your doctor can compare these for trend analysis.")


def _build_doctor_questions(report_values: list, symptoms: list,
                             medications: list, lang: str) -> str:
    questions = []

    abnormal = [v for v in report_values if v.get("status") in ("attention", "abnormal")]

    if lang == "ta":
        if abnormal:
            for v in abnormal[:3]:
                questions.append(
                    f"• என் {v.get('test_name')} மதிப்பு {v.get('result')} {v.get('unit')} — "
                    "இதற்கு என்ன சிகிச்சை தேவை?"
                )
        questions += [
            "• என் தற்போதைய மருந்துகள் சரியானவையா?",
            "• நான் மீண்டும் பரிசோதனை எப்போது செய்ய வேண்டும்?",
            "• என் வாழ்க்கை முறையில் என்ன மாற்றங்கள் செய்ய வேண்டும்?",
        ]
    else:
        if abnormal:
            for v in abnormal[:3]:
                questions.append(
                    f"• My {v.get('test_name')} is {v.get('result')} {v.get('unit')} — "
                    "what treatment or follow-up is needed?"
                )
        questions += [
            "• Are my current medications appropriate?",
            "• When should I repeat these tests?",
            "• What lifestyle changes would you recommend?",
            "• Should I be referred to any specialist?",
        ]

    label = "**மருத்துவரிடம் கேட்க வேண்டிய கேள்விகள்:**" if lang == "ta" else "**Questions to Ask Your Doctor:**"
    return label + "\n" + "\n".join(questions)


def _build_followup_section(report_values: list, lang: str) -> str:
    has_abnormal = any(v.get("status") == "abnormal" for v in report_values)
    has_attention = any(v.get("status") == "attention" for v in report_values)

    if lang == "ta":
        if has_abnormal:
            return "ஒன்று அல்லது அதிகமான அசாதாரண மதிப்புகள் உள்ளன. உங்கள் மருத்துவரிடம் விரைவில் ஆலோசனை பெறுவது பரிந்துரைக்கப்படுகிறது."
        elif has_attention:
            return "சில மதிப்புகள் கவனம் தேவைப்படுகின்றன. அடுத்த வழக்கமான சந்திப்பில் உங்கள் மருத்துவரிடம் இதை பற்றி பேசுங்கள்."
        else:
            return "அனைத்து மதிப்புகளும் சாதாரண வரம்பில் உள்ளன. வழக்கமான கண்காணிப்பை தொடரவும்."
    else:
        if has_abnormal:
            return "One or more values are outside normal range. It is recommended to consult your doctor soon."
        elif has_attention:
            return "Some values need attention. Discuss these with your doctor at your next scheduled visit."
        else:
            return "All values are within normal range. Continue regular monitoring as advised by your doctor."


def _compile_full_text(name: str, sections: dict, lang: str, disclaimer: str) -> str:
    if lang == "ta":
        header = f"# MedVision AI – சுகாதார சுருக்கம்\n**நோயாளி:** {name}\n\n"
    else:
        header = f"# MedVision AI – Health Summary\n**Patient:** {name}\n\n"

    body = "\n\n".join([
        f"## {'1. ' if lang == 'en' else '1. '}Symptoms\n{sections['symptoms']}",
        f"## 2. Report Findings\n{sections['report_findings']}",
        f"## 3. Medications\n{sections['medications']}",
        f"## 4. Warnings\n{sections['warnings']}",
        f"## 5. Historical Changes\n{sections['historical_changes']}",
        f"## 6. Questions for Doctor\n{sections['questions_for_doctor']}",
        f"## 7. Recommended Follow-up\n{sections['recommended_followup']}",
    ])

    return header + body + disclaimer
