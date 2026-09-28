"""
Report Explainer – generates simple-language explanations for lab values.
Uses LLM API if available, otherwise uses a curated knowledge base.
"""
from app.core.config import settings

DISCLAIMER_EN = (
    "\n\n⚠️ IMPORTANT: This explanation is for informational purposes only. "
    "It is NOT a medical diagnosis. Please consult your doctor to understand your results."
)

DISCLAIMER_TA = (
    "\n\n⚠️ முக்கியம்: இந்த விளக்கம் தகவல் நோக்கங்களுக்காக மட்டுமே. "
    "இது மருத்துவ நோயறிதல் அல்ல. உங்கள் முடிவுகளை புரிந்துகொள்ள உங்கள் மருத்துவரை அணுகவும்."
)

# Curated knowledge base for common lab tests
LAB_EXPLANATIONS = {
    "hemoglobin": {
        "en": "Hemoglobin is a protein in your red blood cells that carries oxygen throughout your body. Low levels may indicate anemia.",
        "ta": "ஹீமோகுளோபின் என்பது உங்கள் சிவப்பு இரத்த அணுக்களில் உள்ள ஒரு புரதம், இது உங்கள் உடல் முழுவதும் ஆக்சிஜனை கொண்டு செல்கிறது. குறைந்த அளவுகள் இரத்த சோகையை குறிக்கலாம்.",
    },
    "fasting blood sugar": {
        "en": "Fasting blood sugar measures your blood glucose level after not eating for at least 8 hours. High levels may indicate diabetes or pre-diabetes.",
        "ta": "உண்ணாவிரத இரத்த சர்க்கரை என்பது குறைந்தது 8 மணி நேரம் சாப்பிடாமல் இருந்த பிறகு உங்கள் இரத்த குளுக்கோஸ் அளவை அளவிடுகிறது. அதிக அளவுகள் நீரிழிவு அல்லது முன்-நீரிழிவை குறிக்கலாம்.",
    },
    "hba1c": {
        "en": "HbA1c shows your average blood sugar level over the past 2-3 months. It helps diagnose and monitor diabetes management.",
        "ta": "HbA1c கடந்த 2-3 மாதங்களில் உங்கள் சராசரி இரத்த சர்க்கரை அளவை காட்டுகிறது. நீரிழிவை கண்டறிந்து கண்காணிக்க உதவுகிறது.",
    },
    "total cholesterol": {
        "en": "Cholesterol is a fatty substance in your blood. High total cholesterol increases the risk of heart disease.",
        "ta": "கொழுப்பு என்பது உங்கள் இரத்தத்தில் உள்ள ஒரு கொழுப்பு பொருள். அதிக மொத்த கொழுப்பு இதய நோயின் அபாயத்தை அதிகரிக்கிறது.",
    },
    "ldl cholesterol": {
        "en": "LDL is 'bad' cholesterol. High LDL can build up in arteries and increase the risk of heart disease and stroke.",
        "ta": "LDL என்பது 'கெட்ட' கொழுப்பு. அதிக LDL தமனிகளில் குவிந்து இதய நோய் மற்றும் பக்கவாத அபாயத்தை அதிகரிக்கும்.",
    },
    "hdl cholesterol": {
        "en": "HDL is 'good' cholesterol. Higher HDL levels help remove bad cholesterol and protect against heart disease.",
        "ta": "HDL என்பது 'நல்ல' கொழுப்பு. அதிக HDL அளவுகள் கெட்ட கொழுப்பை அகற்ற உதவுகிறது மற்றும் இதய நோயிலிருந்து பாதுகாக்கிறது.",
    },
    "triglycerides": {
        "en": "Triglycerides are a type of fat in your blood. High levels, combined with high cholesterol, increase heart disease risk.",
        "ta": "ட்ரைகிளிசரைடுகள் உங்கள் இரத்தத்தில் உள்ள ஒரு வகை கொழுப்பு. அதிக கொழுப்புடன் அதிக அளவுகள் இதய நோய் அபாயத்தை அதிகரிக்கும்.",
    },
    "serum creatinine": {
        "en": "Creatinine is a waste product filtered by your kidneys. High levels may indicate kidney problems.",
        "ta": "கிரியேட்டினின் என்பது உங்கள் சிறுநீரகங்களால் வடிகட்டப்படும் கழிவு பொருள். அதிக அளவுகள் சிறுநீரக பிரச்சினைகளை குறிக்கலாம்.",
    },
    "wbc count": {
        "en": "White blood cells are part of your immune system. High or low WBC counts can indicate infections, inflammation, or immune conditions.",
        "ta": "வெள்ளை இரத்த அணுக்கள் உங்கள் நோய் எதிர்ப்பு அமைப்பின் ஒரு பகுதி. அதிக அல்லது குறைந்த WBC எண்ணிக்கை தொற்றுகள், வீக்கம் அல்லது நோய் எதிர்ப்பு நிலைகளை குறிக்கலாம்.",
    },
    "platelet count": {
        "en": "Platelets help your blood clot. Low platelet count can increase bleeding risk; high count may indicate inflammation.",
        "ta": "பிளேட்லெட்டுகள் உங்கள் இரத்தம் உறைய உதவுகின்றன. குறைந்த பிளேட்லெட் எண்ணிக்கை இரத்தப்போக்கு அபாயத்தை அதிகரிக்கலாம்; அதிக எண்ணிக்கை வீக்கத்தை குறிக்கலாம்.",
    },
}

STATUS_EXPLANATIONS = {
    "normal": {
        "en": "This value is within the normal reference range. Continue maintaining a healthy lifestyle.",
        "ta": "இந்த மதிப்பு சாதாரண குறிப்பு வரம்பிற்குள் உள்ளது. ஆரோக்கியமான வாழ்க்கை முறையை தொடர்ந்து பராமரிக்கவும்.",
    },
    "attention": {
        "en": "This value is slightly outside the normal range. It is recommended to discuss this with your doctor.",
        "ta": "இந்த மதிப்பு சாதாரண வரம்பிற்கு சற்று வெளியே உள்ளது. உங்கள் மருத்துவரிடம் இதை பற்றி விவாதிக்க பரிந்துரைக்கப்படுகிறது.",
    },
    "abnormal": {
        "en": "This value is significantly outside the normal range. Please consult your doctor for proper evaluation.",
        "ta": "இந்த மதிப்பு சாதாரண வரம்பிற்கு கணிசமாக வெளியே உள்ளது. சரியான மதிப்பீட்டிற்காக உங்கள் மருத்துவரை கலந்தாலோசிக்கவும்.",
    },
}


def explain_test_value(test_name: str, result: str, unit: str, ref_range: str,
                        status: str, language: str = "en") -> str:
    """Generate a simple-language explanation for a lab test value."""
    lang = language if language in ["en", "ta"] else "en"
    key = test_name.lower().strip()

    # Look up knowledge base
    explanation = ""
    for kb_key, kb_val in LAB_EXPLANATIONS.items():
        if kb_key in key or key in kb_key:
            explanation = kb_val.get(lang, kb_val["en"])
            break

    if not explanation:
        if lang == "ta":
            explanation = f"{test_name} என்பது ஒரு மருத்துவ பரிசோதனை. உங்கள் மருத்துவர் இதன் முக்கியத்துவத்தை விளக்குவார்."
        else:
            explanation = f"{test_name} is a medical test parameter. Your doctor can explain its significance for your specific situation."

    status_msg = STATUS_EXPLANATIONS.get(status, {}).get(lang, "")

    full_explanation = f"{explanation}\n\n{status_msg}"
    disclaimer = DISCLAIMER_TA if lang == "ta" else DISCLAIMER_EN
    return full_explanation + disclaimer


def generate_doctor_questions(report_values: list, language: str = "en") -> list:
    """Generate questions a patient can ask their doctor about their report."""
    abnormal = [v for v in report_values if v.get("status") in ("attention", "abnormal")]
    questions = []

    if language == "ta":
        if abnormal:
            for v in abnormal[:5]:
                questions.append(
                    f"என் {v.get('test_name')} மதிப்பு {v.get('result')} {v.get('unit')} — இது என் உடல்நிலையை பாதிக்குமா?"
                )
        questions += [
            "எனக்கு மேலும் என்ன பரிசோதனைகள் தேவை?",
            "என் உணவு முறை எப்படி இருக்க வேண்டும்?",
            "நான் மீண்டும் பரிசோதனை எப்போது செய்ய வேண்டும்?",
            "என் மருந்துகளை மாற்ற வேண்டுமா?",
        ]
    else:
        if abnormal:
            for v in abnormal[:5]:
                questions.append(
                    f"My {v.get('test_name')} is {v.get('result')} {v.get('unit')} — what does this mean for me?"
                )
        questions += [
            "Do I need any additional tests based on these results?",
            "What dietary changes would you recommend?",
            "When should I repeat these tests?",
            "Do any of these values require a change in my current medications?",
            "Are there any lifestyle changes I should make?",
        ]

    return questions[:8]  # Return max 8 questions


def generate_report_summary(report_values: list, language: str = "en") -> str:
    """Generate a plain-language summary of the report."""
    normal = [v for v in report_values if v.get("status") == "normal"]
    attention = [v for v in report_values if v.get("status") == "attention"]
    abnormal = [v for v in report_values if v.get("status") == "abnormal"]

    if language == "ta":
        summary = f"இந்த அறிக்கையில் {len(report_values)} பரிசோதனைகள் உள்ளன. "
        summary += f"{len(normal)} பரிசோதனைகள் சாதாரண வரம்பில் உள்ளன. "
        if attention:
            summary += f"{len(attention)} பரிசோதனைகள் கவனம் தேவைப்படுகின்றன: "
            summary += ", ".join([v.get("test_name", "") for v in attention]) + ". "
        if abnormal:
            summary += f"{len(abnormal)} பரிசோதனைகள் அசாதாரண அளவில் உள்ளன: "
            summary += ", ".join([v.get("test_name", "") for v in abnormal]) + ". "
        summary += "\n\n⚠️ இந்த சுருக்கம் தகவல் நோக்கங்களுக்காக மட்டுமே. மருத்துவ ஆலோசனைக்கு உங்கள் மருத்துவரை அணுகவும்."
    else:
        summary = f"This report contains {len(report_values)} test results. "
        summary += f"{len(normal)} values are within normal range. "
        if attention:
            summary += f"{len(attention)} values need attention: "
            summary += ", ".join([v.get("test_name", "") for v in attention]) + ". "
        if abnormal:
            summary += f"{len(abnormal)} values are outside normal range: "
            summary += ", ".join([v.get("test_name", "") for v in abnormal]) + ". "
        summary += "\n\n⚠️ This summary is for informational purposes only and does not constitute a medical diagnosis. Please consult your doctor."

    return summary
