"""
AI Chatbot Service – MedVision AI Assistant.
Uses LLM API if configured, otherwise a rule-based fallback.
"""
import re
from app.core.config import settings

SYSTEM_PROMPT_EN = """You are MedVision AI Assistant, a helpful medical information assistant.

IMPORTANT RULES:
1. You NEVER diagnose diseases or medical conditions.
2. You NEVER prescribe medications or recommend dosage changes.
3. You NEVER tell patients to stop prescribed medication.
4. You ALWAYS recommend consulting a qualified doctor for medical decisions.
5. For EMERGENCY symptoms (chest pain, difficulty breathing, severe bleeding, stroke signs), 
   immediately direct the user to call emergency services.
6. You provide educational information about medical terms, test results, and general health.
7. Always add a disclaimer that your responses are informational only.
8. You are respectful, compassionate, and non-judgmental.

You can help with:
- Explaining medical terminology in simple language
- General information about common medicines (not prescribing them)
- Explaining lab test results in plain language
- Generating questions to ask the doctor
- General health and wellness information

Always end responses with: "⚠️ This information is educational only. Please consult your doctor for medical advice."
"""

SYSTEM_PROMPT_TA = """நீங்கள் MedVision AI உதவியாளர், ஒரு பயனுள்ள மருத்துவ தகவல் உதவியாளர்.

முக்கியமான விதிகள்:
1. நீங்கள் ஒருபோதும் நோய்களை கண்டறிவதில்லை.
2. நீங்கள் ஒருபோதும் மருந்துகளை பரிந்துரைப்பதில்லை.
3. நீங்கள் ஒருபோதும் நோயாளிகளை பரிந்துரைக்கப்பட்ட மருந்தை நிறுத்தச் சொல்வதில்லை.
4. மருத்துவ தீர்மானங்களுக்கு நீங்கள் எப்போதும் தகுதி வாய்ந்த மருத்துவரை அணுக பரிந்துரைக்கிறீர்கள்.
5. அவசரகால அறிகுறிகளுக்கு, உடனடியாக அவசர சேவைகளை அழைக்க வழிகாட்டுங்கள்.

⚠️ இந்த தகவல் கல்வி நோக்கங்களுக்காக மட்டுமே. மருத்துவ ஆலோசனைக்கு உங்கள் மருத்துவரை அணுகவும்.
"""

EMERGENCY_KEYWORDS = [
    "chest pain", "heart attack", "can't breathe", "cannot breathe", "difficulty breathing",
    "severe bleeding", "unconscious", "stroke", "paralysis", "seizure", "overdose",
    "poisoning", "severe allergic reaction", "anaphylaxis",
    # Tamil emergency keywords
    "நெஞ்சு வலி", "மூச்சு விட முடியவில்லை", "மயக்கம்", "வலிப்பு",
]

EMERGENCY_RESPONSE_EN = (
    "🚨 **EMERGENCY ALERT** 🚨\n\n"
    "The symptoms you described may require immediate medical attention.\n\n"
    "**Please take these steps immediately:**\n"
    "1. Call emergency services: **112** (India) or your local emergency number\n"
    "2. If in a hospital, alert the nearest staff immediately\n"
    "3. Do not drive yourself to the hospital\n\n"
    "This assistant cannot provide emergency medical care. "
    "Please seek immediate professional help."
)

EMERGENCY_RESPONSE_TA = (
    "🚨 **அவசர எச்சரிக்கை** 🚨\n\n"
    "நீங்கள் விவரித்த அறிகுறிகளுக்கு உடனடி மருத்துவ கவனிப்பு தேவைப்படலாம்.\n\n"
    "**உடனடியாக இந்த படிகளை எடுக்கவும்:**\n"
    "1. அவசர சேவைகளை அழைக்கவும்: **112** (இந்தியா)\n"
    "2. மருத்துவமனையில் இருந்தால், அருகிலுள்ள ஊழியரை உடனே அறிவிக்கவும்\n\n"
    "இந்த உதவியாளர் அவசர மருத்துவ சேவை வழங்க முடியாது. "
    "உடனடி தொழில்முறை உதவியை நாடுங்கள்."
)

# Simple rule-based FAQ knowledge base
KNOWLEDGE_BASE = {
    "hemoglobin": {
        "en": "Hemoglobin is a protein in red blood cells that carries oxygen throughout the body. Normal range: Men 13.5-17.5 g/dL, Women 12.0-15.5 g/dL.",
        "ta": "ஹீமோகுளோபின் என்பது சிவப்பு இரத்த அணுக்களில் உள்ள ஒரு புரதம். சாதாரண வரம்பு: ஆண்கள் 13.5-17.5 g/dL, பெண்கள் 12.0-15.5 g/dL.",
    },
    "diabetes": {
        "en": "Diabetes is a condition where blood sugar levels are too high. It requires medical management including diet, exercise, and often medication. Please consult your doctor.",
        "ta": "நீரிழிவு என்பது இரத்த சர்க்கரை அளவு மிக அதிகமாக இருக்கும் ஒரு நிலை. உணவு, உடற்பயிற்சி மற்றும் பெரும்பாலும் மருந்துகள் உட்பட மருத்துவ மேலாண்மை தேவைப்படுகிறது.",
    },
    "blood pressure": {
        "en": "Blood pressure measures the force of blood against artery walls. Normal: below 120/80 mmHg. High blood pressure (hypertension) should be managed under a doctor's guidance.",
        "ta": "இரத்த அழுத்தம் தமனி சுவர்களுக்கு எதிராக இரத்தத்தின் விசையை அளவிடுகிறது. சாதாரண: 120/80 mmHg க்கு கீழே.",
    },
    "cholesterol": {
        "en": "Cholesterol is a waxy substance in blood. High LDL ('bad') cholesterol can increase heart disease risk. Healthy lifestyle and sometimes medication help manage it.",
        "ta": "கொழுப்பு இரத்தத்தில் ஒரு மெழுகு பொருள். அதிக LDL கொழுப்பு இதய நோய் அபாயத்தை அதிகரிக்கும்.",
    },
}

DISCLAIMER_EN = "\n\n⚠️ This information is educational only. Please consult your doctor for medical advice."
DISCLAIMER_TA = "\n\n⚠️ இந்த தகவல் கல்வி நோக்கங்களுக்காக மட்டுமே. மருத்துவ ஆலோசனைக்கு உங்கள் மருத்துவரை அணுகவும்."


def is_emergency(message: str) -> bool:
    message_lower = message.lower()
    return any(kw in message_lower for kw in EMERGENCY_KEYWORDS)


def get_chatbot_response(message: str, language: str = "en",
                          conversation_history: list = None) -> dict:
    """Get a chatbot response for the given message."""
    lang = language if language in ["en", "ta"] else "en"

    # Check for emergency
    if is_emergency(message):
        return {
            "response": EMERGENCY_RESPONSE_TA if lang == "ta" else EMERGENCY_RESPONSE_EN,
            "is_emergency": True,
            "has_disclaimer": True,
            "confidence": 1.0,
        }

    # Try LLM API first
    if settings.OPENAI_API_KEY:
        try:
            response = _get_openai_response(message, lang, conversation_history)
            return {
                "response": response + (DISCLAIMER_TA if lang == "ta" else DISCLAIMER_EN),
                "is_emergency": False,
                "has_disclaimer": True,
                "confidence": 0.9,
            }
        except Exception:
            pass

    # Rule-based fallback
    response = _rule_based_response(message, lang)
    return {
        "response": response,
        "is_emergency": False,
        "has_disclaimer": True,
        "confidence": 0.7,
    }


def _get_openai_response(message: str, language: str, history: list = None) -> str:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        system_prompt = SYSTEM_PROMPT_TA if language == "ta" else SYSTEM_PROMPT_EN
        messages = [{"role": "system", "content": system_prompt}]

        if history:
            for h in history[-6:]:  # Last 6 messages for context
                messages.append({"role": h["role"], "content": h["message"]})

        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise e


def _rule_based_response(message: str, language: str) -> str:
    message_lower = message.lower()
    disclaimer = DISCLAIMER_TA if language == "ta" else DISCLAIMER_EN

    for keyword, responses in KNOWLEDGE_BASE.items():
        if keyword in message_lower:
            return responses.get(language, responses["en"]) + disclaimer

    # Generic response
    if language == "ta":
        return (
            "உங்கள் கேள்விக்கு நன்றி. நான் மருத்துவ சொற்கள், ஆய்வக முடிவுகள் மற்றும் பொதுவான "
            "சுகாதார தகவல்களை விளக்க உதவ முடியும். மருத்துவ ஆலோசனைக்கு, தயவுசெய்து உங்கள் "
            "மருத்துவரை அணுகவும்." + disclaimer
        )
    else:
        return (
            "Thank you for your question. I can help explain medical terminology, "
            "lab results, and general health information. "
            "For medical advice specific to your condition, please consult your doctor." + disclaimer
        )
