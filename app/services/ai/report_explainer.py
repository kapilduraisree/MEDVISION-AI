"""
MedVision AI – Report Explainer (v2)
Generates plain-language explanations for individual lab values.
Uses the unified LLM client if available; falls back to curated knowledge base.
"""
from app.core.config import settings

DISCLAIMER_EN = (
    "\n\n**Important:** This explanation is for informational purposes only. "
    "It is NOT a medical diagnosis. Please consult your doctor to understand your results."
)
DISCLAIMER_TA = (
    "\n\n**முக்கியம்:** இந்த விளக்கம் தகவல் நோக்கங்களுக்காக மட்டுமே. "
    "இது மருத்துவ நோயறிதல் அல்ல. உங்கள் மருத்துவரை அணுகவும்."
)

LAB_EXPLANATIONS = {
    "hemoglobin": {
        "en": "Hemoglobin is a protein in red blood cells that carries oxygen. Low levels may indicate anaemia.",
        "ta": "ஹீமோகுளோபின் சிவப்பு இரத்த அணுக்களில் ஆக்சிஜனை கொண்டு செல்லும் புரதம். குறைந்த அளவுகள் இரத்த சோகையை குறிக்கலாம்.",
    },
    "fasting blood sugar": {
        "en": "Fasting blood sugar measures blood glucose after 8 hours without eating. High values may indicate diabetes.",
        "ta": "உண்ணாவிரத இரத்த சர்க்கரை 8 மணி நேரம் சாப்பிடாமல் இரத்த குளுக்கோஸை அளவிடுகிறது.",
    },
    "hba1c": {
        "en": "HbA1c reflects your average blood sugar over 2–3 months. It's used to diagnose and monitor diabetes control.",
        "ta": "HbA1c கடந்த 2–3 மாதங்களில் சராசரி இரத்த சர்க்கரையை காட்டுகிறது.",
    },
    "total cholesterol": {
        "en": "Total cholesterol measures all fats in the blood. High levels increase heart disease risk.",
        "ta": "மொத்த கொழுப்பு இரத்தத்தில் உள்ள அனைத்து கொழுப்புகளையும் அளவிடுகிறது.",
    },
    "ldl cholesterol": {
        "en": "LDL is 'bad' cholesterol that can build up in artery walls, increasing heart attack and stroke risk.",
        "ta": "LDL கெட்ட கொழுப்பு; தமனி சுவர்களில் குவிந்து இதய நோய் அபாயத்தை அதிகரிக்கும்.",
    },
    "hdl cholesterol": {
        "en": "HDL is 'good' cholesterol that helps remove bad cholesterol. Higher levels are protective.",
        "ta": "HDL நல்ல கொழுப்பு; கெட்ட கொழுப்பை அகற்ற உதவுகிறது.",
    },
    "triglycerides": {
        "en": "Triglycerides are blood fats. High levels combined with high cholesterol increase cardiovascular risk.",
        "ta": "ட்ரைகிளிசரைடுகள் இரத்தத்தில் உள்ள கொழுப்பு வகை. அதிக அளவுகள் இதய நோய் அபாயத்தை அதிகரிக்கும்.",
    },
    "serum creatinine": {
        "en": "Creatinine is filtered by the kidneys. Elevated levels may indicate reduced kidney function.",
        "ta": "கிரியேட்டினின் சிறுநீரகங்களால் வடிகட்டப்படும் கழிவு. அதிக அளவுகள் சிறுநீரக பிரச்சினைகளை குறிக்கலாம்.",
    },
    "wbc count": {
        "en": "White blood cells fight infection. Abnormal counts (high or low) can indicate infections, autoimmune conditions, or other issues.",
        "ta": "வெள்ளை இரத்த அணுக்கள் தொற்றுகளை எதிர்க்கின்றன. அசாதாரண எண்ணிக்கை பல்வேறு நிலைகளை குறிக்கலாம்.",
    },
    "platelet count": {
        "en": "Platelets help blood clot. Low count raises bleeding risk; high count may indicate inflammation or clotting disorders.",
        "ta": "பிளேட்லெட்டுகள் இரத்தம் உறைய உதவுகின்றன.",
    },
    "blood urea nitrogen": {
        "en": "BUN measures protein breakdown waste filtered by the kidneys. High levels may suggest kidney or liver problems.",
        "ta": "BUN புரத சிதைவிலிருந்து வரும் கழிவை அளவிடுகிறது.",
    },
    "sgot": {
        "en": "SGOT (AST) is an enzyme found in the liver and heart. Elevated levels may indicate liver damage or muscle injury.",
        "ta": "SGOT கல்லீரல் மற்றும் இதயத்தில் உள்ள என்சைம். அதிக அளவுகள் கல்லீரல் சேதத்தை குறிக்கலாம்.",
    },
    "sgpt": {
        "en": "SGPT (ALT) is a liver-specific enzyme. Elevated levels strongly suggest liver inflammation or damage.",
        "ta": "SGPT கல்லீரல் குறிப்பிட்ட என்சைம். உயர்ந்த அளவுகள் கல்லீரல் வீக்கம் அல்லது சேதத்தை குறிக்கும்.",
    },
    "vitamin b12": {
        "en": "Vitamin B12 is essential for nerve function and red blood cell production. Low levels cause anaemia and neurological symptoms.",
        "ta": "வைட்டமின் B12 நரம்பு செயல்பாட்டிற்கு அவசியம். குறைபாடு இரத்த சோகையை ஏற்படுத்துகிறது.",
    },
    "tsh": {
        "en": "TSH (Thyroid Stimulating Hormone) controls thyroid activity. High TSH usually means the thyroid is underactive (hypothyroidism); low TSH means overactive (hyperthyroidism).",
        "ta": "TSH தைராய்டு சுரப்பியை கட்டுப்படுத்துகிறது. அதிக TSH ஹைப்போதைராய்டிசத்தை குறிக்கும்.",
    },
    "egfr": {
        "en": "eGFR (estimated Glomerular Filtration Rate) measures kidney filtering efficiency. Normal is above 60; lower values indicate chronic kidney disease stages.",
        "ta": "eGFR சிறுநீரக வடிகட்டல் திறனை அளவிடுகிறது. 60-ஐ விட குறைவான மதிப்புகள் சிறுநீரக நோயை குறிக்கலாம்.",
    },
}

STATUS_EXPLANATIONS = {
    "normal": {
        "en": "✅ This value is within the normal reference range. Continue maintaining a healthy lifestyle.",
        "ta": "✅ இந்த மதிப்பு சாதாரண வரம்பிற்குள் உள்ளது.",
    },
    "attention": {
        "en": "🟡 This value is slightly outside the normal range. Please discuss this with your doctor.",
        "ta": "🟡 இந்த மதிப்பு சாதாரண வரம்பிற்கு சற்று வெளியே உள்ளது. மருத்துவரிடம் விவாதிக்கவும்.",
    },
    "abnormal": {
        "en": "🔴 This value is significantly outside the normal range. Please consult your doctor for evaluation.",
        "ta": "🔴 இந்த மதிப்பு சாதாரண வரம்பிற்கு கணிசமாக வெளியே உள்ளது. மருத்துவரை கலந்தாலோசிக்கவும்.",
    },
}


def explain_test_value(
    test_name: str,
    result: str,
    unit: str,
    ref_range: str,
    status: str,
    language: str = "en",
    use_llm: bool = True,
) -> str:
    """
    Generate a plain-language explanation for a single lab test value.
    Tries LLM first (for rich, context-aware explanation) then falls back to knowledge base.
    """
    lang = language if language in ("en", "ta") else "en"
    disclaimer = DISCLAIMER_TA if lang == "ta" else DISCLAIMER_EN
    status_msg = STATUS_EXPLANATIONS.get(status, {}).get(lang, "")

    # Try LLM for a rich, personalised explanation
    if use_llm:
        try:
            from app.services.ai.llm_client import llm_complete, active_provider
            if active_provider() != "none":
                lang_instr = "Respond in Tamil." if lang == "ta" else "Respond in English."
                prompt = (
                    f"Explain this lab test result to a patient in simple, clear language (2-3 sentences):\n"
                    f"Test: {test_name}\n"
                    f"Result: {result} {unit}\n"
                    f"Reference range: {ref_range}\n"
                    f"Status: {status}\n"
                    f"{lang_instr}\n"
                    f"Do not diagnose. Do not prescribe. State the status clearly."
                )
                llm_text = llm_complete(prompt, max_tokens=200, temperature=0.3)
                return f"{llm_text}\n\n{status_msg}{disclaimer}"
        except Exception:
            pass

    # Knowledge-base fallback
    key = test_name.lower().strip()
    kb_explanation = ""
    for kb_key, kb_val in LAB_EXPLANATIONS.items():
        if kb_key in key or key in kb_key:
            kb_explanation = kb_val.get(lang, kb_val["en"])
            break

    if not kb_explanation:
        if lang == "ta":
            kb_explanation = f"{test_name} ஒரு மருத்துவ பரிசோதனை அளவீடு. உங்கள் மருத்துவர் இதன் முக்கியத்துவத்தை விளக்குவார்."
        else:
            kb_explanation = f"{test_name} is a medical test parameter. Your doctor can explain its significance for your specific situation."

    full = f"{kb_explanation}\n\n{status_msg}"
    return full + disclaimer


def generate_doctor_questions(report_values: list, language: str = "en") -> list:
    """Generate questions a patient can ask their doctor about their report."""
    abnormal = [v for v in report_values if v.get("status") in ("attention", "abnormal")]
    questions = []
    if language == "ta":
        for v in abnormal[:5]:
            questions.append(
                f"என் {v.get('test_name')} மதிப்பு {v.get('result')} {v.get('unit','')} — இது என் உடல்நிலையை பாதிக்குமா?"
            )
        questions += [
            "எனக்கு மேலும் என்ன பரிசோதனைகள் தேவை?",
            "என் உணவு முறை எப்படி இருக்க வேண்டும்?",
            "நான் மீண்டும் பரிசோதனை எப்போது செய்ய வேண்டும்?",
            "என் மருந்துகளை மாற்ற வேண்டுமா?",
        ]
    else:
        for v in abnormal[:5]:
            questions.append(
                f"My {v.get('test_name')} is {v.get('result')} {v.get('unit','')} — what does this mean for me specifically?"
            )
        questions += [
            "Do I need any follow-up tests based on these results?",
            "What dietary changes would you recommend?",
            "When should I repeat these tests?",
            "Do any values suggest I should change my current medications?",
            "Are there lifestyle changes I should make?",
        ]
    return questions[:8]


def generate_report_summary(report_values: list, language: str = "en") -> str:
    """Generate a plain-language summary of all lab values in a report."""
    normal    = [v for v in report_values if v.get("status") == "normal"]
    attention = [v for v in report_values if v.get("status") == "attention"]
    abnormal  = [v for v in report_values if v.get("status") == "abnormal"]

    # Try LLM for a richer narrative summary
    try:
        from app.services.ai.llm_client import llm_complete, active_provider
        if active_provider() != "none" and report_values:
            lang_instr = "Respond in Tamil." if language == "ta" else "Respond in English."
            lines = [f"Summarise these lab results in 3–4 plain sentences for a patient. {lang_instr}"]
            lines.append(f"Total: {len(report_values)} tests. Normal: {len(normal)}. Needs attention: {len(attention)}. Abnormal: {len(abnormal)}.")
            if attention:
                lines.append("Attention: " + ", ".join(v.get("test_name","") for v in attention))
            if abnormal:
                lines.append("Abnormal: " + ", ".join(
                    f"{v.get('test_name')} ({v.get('result')} {v.get('unit','')})" for v in abnormal
                ))
            lines.append("Do not diagnose. End with a reminder to discuss with their doctor.")
            llm_text = llm_complete("\n".join(lines), max_tokens=250, temperature=0.3)
            disclaimer = settings.AI_DISCLAIMER_TA if language == "ta" else settings.AI_DISCLAIMER_EN
            return llm_text + f"\n\n{disclaimer}"
    except Exception:
        pass

    # Rule-based fallback
    if language == "ta":
        s = f"இந்த அறிக்கையில் **{len(report_values)}** பரிசோதனைகள் உள்ளன. **{len(normal)}** சாதாரண வரம்பில் உள்ளன. "
        if attention:
            s += f"**{len(attention)}** கவனம் தேவை: " + ", ".join(v.get("test_name","") for v in attention) + ". "
        if abnormal:
            s += f"**{len(abnormal)}** அசாதாரண அளவில்: " + ", ".join(v.get("test_name","") for v in abnormal) + ". "
        s += "\n\n⚠️ இந்த சுருக்கம் தகவல் நோக்கங்களுக்காக மட்டுமே. மருத்துவ ஆலோசனைக்கு மருத்துவரை அணுகவும்."
    else:
        s = f"This report has **{len(report_values)}** results. **{len(normal)}** within normal range. "
        if attention:
            s += f"**{len(attention)}** need attention: " + ", ".join(v.get("test_name","") for v in attention) + ". "
        if abnormal:
            s += f"**{len(abnormal)}** outside normal: " + ", ".join(v.get("test_name","") for v in abnormal) + ". "
        s += "\n\n⚠️ This summary is informational only. Please consult your doctor."
    return s
