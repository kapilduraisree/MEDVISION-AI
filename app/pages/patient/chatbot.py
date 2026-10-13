"""
AI Chatbot - bilingual (English/Tamil) medical information assistant.
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.utils import section_header, ai_disclaimer
from app.services.ai.chatbot_service import get_chatbot_response, is_emergency


def show():
    user = require_auth(["patient","doctor","admin"])
    lang = user["language"]

    section_header("🤖 AI Health Assistant", "Ask questions about medicines, reports, and health")
    ai_disclaimer(lang)

    # Language toggle
    lang_options = {"English": "en", "Tamil (தமிழ்)": "ta"}
    selected_lang_label = st.selectbox(
        "Response Language",
        list(lang_options.keys()),
        index=0 if lang == "en" else 1,
    )
    active_lang = lang_options[selected_lang_label]

    # Session chat history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Render existing messages
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Suggested questions
    if not st.session_state["chat_history"]:
        st.markdown("**💡 Try asking:**")
        suggestions = [
            "What does HbA1c mean?",
            "Explain high LDL cholesterol",
            "What is hemoglobin?",
            "How to manage blood pressure?",
        ]
        cols = st.columns(2)
        for i, suggestion in enumerate(suggestions):
            with cols[i % 2]:
                if st.button(suggestion, key=f"sug_{i}"):
                    _send_message(suggestion, active_lang, user)
                    st.rerun()

    # Input
    user_input = st.chat_input("Ask a medical question…")
    if user_input:
        _send_message(user_input, active_lang, user)
        st.rerun()

    # Clear button
    if st.session_state["chat_history"]:
        if st.button("🗑️ Clear Chat", use_container_width=False):
            st.session_state["chat_history"] = []
            st.rerun()


def _send_message(message: str, lang: str, user: dict):
    # Add user message
    st.session_state["chat_history"].append({"role": "user", "content": message})

    # Build history for context
    history = [
        {"role": m["role"], "message": m["content"]}
        for m in st.session_state["chat_history"][-10:]
    ]

    # Get AI response
    result = get_chatbot_response(message, lang, history)
    response = result.get("response", "Sorry, I could not process that request.")

    # Save to DB (best effort)
    try:
        from app.core.database import execute_write
        uid = user.get("id")
        if uid:
            execute_write(
                """INSERT INTO chatbot_history
                   (user_id, role, message, language, is_ai_response, has_disclaimer, created_at)
                   VALUES (:uid,'user',:msg,:lang,FALSE,FALSE,NOW())""",
                {"uid": uid, "msg": message, "lang": lang},
            )
            execute_write(
                """INSERT INTO chatbot_history
                   (user_id, role, message, language, is_ai_response, has_disclaimer, created_at)
                   VALUES (:uid,'assistant',:msg,:lang,TRUE,TRUE,NOW())""",
                {"uid": uid, "msg": response, "lang": lang},
            )
    except Exception:
        pass

    st.session_state["chat_history"].append({"role": "assistant", "content": response})

    # Flash emergency alert separately
    if result.get("is_emergency"):
        st.session_state["show_emergency"] = True
