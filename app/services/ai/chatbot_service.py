"""
MedVision AI – Chatbot Service (v2)
Routes every query through:
  1. Emergency keyword check (immediate 112 alert)
  2. RAG retrieval over patient records (if patient_id provided)
  3. Unified LLM client (Gemini → OpenAI → Ollama → rule-based fallback)

get_chatbot_response() is backward-compatible with v1 callers.
get_rag_response()     is the new RAG-aware entry point.
"""
from app.core.config import settings

# ── Medical safety constants ──────────────────────────────────────────────────
EMERGENCY_KEYWORDS = [
    "chest pain", "heart attack", "cant breathe", "cannot breathe",
    "difficulty breathing", "severe bleeding", "unconscious", "stroke",
    "paralysis", "seizure", "overdose", "poisoning", "anaphylaxis",
    "severe allergic reaction",
    "நெஞ்சு வலி", "மூச்சு விட முடியவில்லை", "மயக்கம்", "வலிப்பு",
]

EMERGENCY_RESPONSE_EN = (
    "🚨 **EMERGENCY ALERT** 🚨\n\n"
    "The symptoms you described may require **immediate medical attention**.\n\n"
    "**Please act now:**\n"
    "1. Call **112** (India) or your local emergency number immediately\n"
    "2. If near a hospital, alert staff immediately\n"
    "3. Do not drive yourself to the hospital\n\n"
    "This assistant cannot provide emergency medical care. Seek help immediately."
)

EMERGENCY_RESPONSE_TA = (
    "🚨 **அவசர எச்சரிக்கை** 🚨\n\n"
    "நீங்கள் விவரித்த அறிகுறிகளுக்கு **உடனடி மருத்துவ கவனிப்பு** தேவைப்படலாம்.\n\n"
    "**உடனடியாக செய்யவும்:**\n"
    "1. **112** (இந்தியா) உடனே அழைக்கவும்\n"
    "2. மருத்துவமனையில் இருந்தால் ஊழியரை அறிவிக்கவும்\n\n"
    "இந்த உதவியாளர் அவசர மருத்துவ சேவை வழங்க முடியாது."
)

SYSTEM_PROMPT_EN = """You are MedVision AI Assistant, a bilingual medical information assistant.

STRICT NON-NEGOTIABLE RULES:
1. Never diagnose any disease or medical condition.
2. Never prescribe medications, doses, or schedules.
3. Never advise stopping a prescribed medication.
4. For ANY emergency symptom, immediately direct the user to call 112.
5. Always recommend consulting a qualified doctor for decisions.
6. Label every response: "This is educational information only."
7. Be compassionate, clear, and jargon-free.

You CAN help with:
- Explaining medical test results and terminology in plain language
- Describing what a medicine is generally used for (not prescribing it)
- General health, nutrition, and wellness information
- Helping patients prepare questions for their doctor
- Explaining what symptoms typically warrant urgent care
"""

SYSTEM_PROMPT_TA = SYSTEM_PROMPT_EN + "\nAlways respond in Tamil (தமிழ்).\n"

DISCLAIMER_EN = "\n\n⚠️ This information is educational only. Please consult your doctor for medical advice."
DISCLAIMER_TA = "\n\n⚠️ இந்த தகவல் கல்வி நோக்கங்களுக்காக மட்டுமே. மருத்துவ ஆலோசனைக்கு மருத்துவரை அணுகவும்."

# ── Rule-based knowledge base (fallback when no LLM) ─────────────────────────
KNOWLEDGE_BASE = {
    "hemoglobin": {
        "en": "Hemoglobin carries oxygen in red blood cells. Normal: Men 13.5–17.5 g/dL, Women 12.0–15.5 g/dL. Low levels may indicate anaemia.",
        "ta": "ஹீமோகுளோபின் சிவப்பு இரத்த அணுக்களில் ஆக்சிஜனை கொண்டு செல்கிறது. சாதாரண வரம்பு: ஆண்கள் 13.5–17.5 g/dL, பெண்கள் 12.0–15.5 g/dL.",
    },
    "diabetes": {
        "en": "Diabetes is a chronic condition where blood sugar is too high. Types 1, 2 and gestational all require medical management.",
        "ta": "நீரிழிவு என்பது இரத்த சர்க்கரை அளவு தொடர்ச்சியாக அதிகமாக இருக்கும் நிலை. மருத்துவ மேலாண்மை தேவைப்படுகிறது.",
    },
    "blood pressure": {
        "en": "Normal blood pressure is below 120/80 mmHg. Hypertension (high BP) must be managed under a doctor's supervision.",
        "ta": "சாதாரண இரத்த அழுத்தம் 120/80 mmHg க்கு கீழே. உயர் இரத்த அழுத்தத்தை மருத்துவரின் கண்காணிப்பில் நிர்வகிக்க வேண்டும்.",
    },
    "cholesterol": {
        "en": "High LDL (bad) cholesterol increases heart disease risk. Diet, exercise, and sometimes statins help manage it.",
        "ta": "அதிக LDL கொழுப்பு இதய நோய் அபாயத்தை அதிகரிக்கும். உணவு, உடற்பயிற்சி, சில நேரங்களில் ஸ்டேட்டின்கள் உதவுகின்றன.",
    },
    "thyroid": {
        "en": "The thyroid regulates metabolism. TSH, T3, T4 tests check its function. Both hypo and hyperthyroidism are treatable.",
        "ta": "தைராய்டு வளர்சிதை மாற்றத்தை கட்டுப்படுத்துகிறது. TSH, T3, T4 சோதனைகள் செயல்பாட்டை சரிபார்க்கின்றன.",
    },
    "hba1c": {
        "en": "HbA1c reflects average blood sugar over 2–3 months. Below 5.7% is normal; 5.7–6.4% is pre-diabetes; 6.5%+ is diabetes.",
        "ta": "HbA1c கடந்த 2–3 மாதங்களில் சராசரி இரத்த சர்க்கரையை காட்டுகிறது. 5.7% க்கு கீழே சாதாரணம்.",
    },
    "anemia": {
        "en": "Anaemia means fewer red blood cells or less haemoglobin. Common causes: iron, B12, or folate deficiency. Symptoms: fatigue, pallor, breathlessness.",
        "ta": "இரத்த சோகை என்பது சிவப்பு அணுக்கள் குறைவாக இருப்பது. இரும்பு, B12 குறைபாடு பொதுவான காரணங்கள்.",
    },
    "kidney": {
        "en": "Key kidney tests: creatinine, BUN, eGFR. High creatinine or low eGFR may indicate kidney dysfunction.",
        "ta": "சிறுநீரக சோதனைகள்: கிரியேட்டினின், BUN, eGFR. அதிக கிரியேட்டினின் சிறுநீரக பிரச்சினைகளை குறிக்கலாம்.",
    },
    "liver": {
        "en": "Liver tests: ALT, AST, ALP, bilirubin. Elevated ALT/AST often indicates liver inflammation or damage.",
        "ta": "கல்லீரல் சோதனைகள்: ALT, AST, ALP. உயர்ந்த ALT/AST கல்லீரல் வீக்கம் அல்லது சேதத்தை குறிக்கும்.",
    },
    "vitamin d": {
        "en": "Vitamin D is essential for bone health and immunity. Normal: 30–100 ng/mL. Deficiency is common and usually treated with supplements.",
        "ta": "வைட்டமின் D எலும்பு ஆரோக்கியத்திற்கு அவசியம். குறைபாடு பொதுவானது மற்றும் சப்ளிமெண்ட்களால் சிகிச்சையளிக்கப்படுகிறது.",
    },
    "creatinine": {
        "en": "Creatinine is a waste product filtered by the kidneys. Normal: 0.6–1.2 mg/dL. High levels may indicate reduced kidney function.",
        "ta": "கிரியேட்டினின் சிறுநீரகங்களால் வடிகட்டப்படும் கழிவு. 0.6–1.2 mg/dL சாதாரணம்.",
    },
}

# ── Public entry points ───────────────────────────────────────────────────────

def is_emergency(message: str) -> bool:
    msg = message.lower().replace("'", "").replace(",", "")
    return any(kw in msg for kw in EMERGENCY_KEYWORDS)


def get_chatbot_response(
    message: str,
    language: str = "en",
    conversation_history: list = None,
    patient_id: int = None,
) -> dict:
    """
    Main chatbot entry point. Backward-compatible with v1.
    Automatically uses RAG context if patient_id is supplied and RAG is available.
    Returns {"response", "is_emergency", "has_disclaimer", "confidence", "provider"}
    """
    lang = language if language in ("en", "ta") else "en"

    # 1. Emergency check always first
    if is_emergency(message):
        return {
            "response":     EMERGENCY_RESPONSE_TA if lang == "ta" else EMERGENCY_RESPONSE_EN,
            "is_emergency": True,
            "has_disclaimer": True,
            "confidence":   1.0,
            "provider":     "safety_guard",
        }

    # 2. RAG-aware LLM path
    if patient_id:
        try:
            from app.services.ai.rag_engine import rag_answer
            response = rag_answer(message, patient_id, language=lang)
            return {
                "response":     response,
                "is_emergency": False,
                "has_disclaimer": True,
                "confidence":   0.95,
                "provider":     _provider_name(),
            }
        except RuntimeError:
            pass   # No LLM configured — fall through to plain LLM / rule-based
        except Exception:
            pass

    # 3. Plain LLM path (no RAG)
    try:
        from app.services.ai.llm_client import llm_chat
        system = SYSTEM_PROMPT_TA if lang == "ta" else SYSTEM_PROMPT_EN
        messages = _build_messages(message, conversation_history)
        response = llm_chat(messages, system=system, max_tokens=600, temperature=0.5)
        disclaimer = DISCLAIMER_TA if lang == "ta" else DISCLAIMER_EN
        return {
            "response":     response + disclaimer,
            "is_emergency": False,
            "has_disclaimer": True,
            "confidence":   0.9,
            "provider":     _provider_name(),
        }
    except RuntimeError:
        pass   # No LLM — fall through to rule-based
    except Exception:
        pass

    # 4. Rule-based fallback
    response = _rule_based_response(message, lang)
    return {
        "response":     response,
        "is_emergency": False,
        "has_disclaimer": True,
        "confidence":   0.6,
        "provider":     "rule_based",
    }


def get_rag_response(
    message: str,
    patient_id: int,
    language: str = "en",
    conversation_history: list = None,
) -> dict:
    """
    Explicit RAG-aware entry point for the dedicated RAG chatbot page.
    Always builds patient context before calling the LLM.
    """
    return get_chatbot_response(
        message,
        language=language,
        conversation_history=conversation_history,
        patient_id=patient_id,
    )


# ── Private helpers ───────────────────────────────────────────────────────────

def _provider_name() -> str:
    try:
        from app.services.ai.llm_client import provider_label
        return provider_label()
    except Exception:
        return "unknown"


def _build_messages(message: str, history: list = None) -> list:
    messages = []
    if history:
        for h in history[-8:]:
            role = h.get("role", "user")
            content = h.get("content", h.get("message", ""))
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": message})
    return messages


def _rule_based_response(message: str, language: str) -> str:
    msg_lower = message.lower()
    disclaimer = DISCLAIMER_TA if language == "ta" else DISCLAIMER_EN
    for keyword, responses in KNOWLEDGE_BASE.items():
        if keyword in msg_lower:
            return responses.get(language, responses["en"]) + disclaimer
    if language == "ta":
        return (
            "உங்கள் கேள்விக்கு நன்றி. மருத்துவ சொற்கள், ஆய்வக முடிவுகள் மற்றும் "
            "பொதுவான சுகாதார தகவல்களை விளக்க உதவ முடியும். "
            "மருத்துவ ஆலோசனைக்கு மருத்துவரை அணுகவும்." + disclaimer
        )
    return (
        "Thank you for your question. I can help explain medical terminology, "
        "lab results, and general health information. "
        "For advice specific to your condition, please consult your doctor." + disclaimer
    )
