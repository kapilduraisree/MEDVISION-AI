"""
MedVision AI – RAG Health Assistant Page
The patient asks questions and the LLM answers using THEIR OWN health records as context.
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.utils import section_header, ai_disclaimer
from app.services.ai.rag_engine import (
    build_patient_index, retrieve, index_stats, rag_answer, RAG_AVAILABLE
)
from app.services.ai.chatbot_service import is_emergency, EMERGENCY_RESPONSE_EN, EMERGENCY_RESPONSE_TA
from app.services.ai.llm_client import active_provider, provider_label


# ── Suggested questions by category ──────────────────────────────────────────
SUGGESTIONS = {
    "📊 My Lab Results": [
        "Which of my lab values are outside the normal range?",
        "What does my HbA1c result mean?",
        "Has my cholesterol improved compared to my last report?",
        "Are any of my kidney function values concerning?",
    ],
    "💊 My Medications": [
        "What medications am I currently taking?",
        "Are there any potential interactions between my medicines?",
        "What is Metformin used for?",
        "Should I take my medicines before or after food?",
    ],
    "🩺 My Symptoms": [
        "I logged fatigue and headache — what could cause these?",
        "Are my recent symptoms related to my known conditions?",
        "What symptoms should prompt me to see a doctor urgently?",
    ],
    "📋 General Health": [
        "Give me an overview of my overall health status.",
        "What lifestyle changes would help based on my records?",
        "When should I schedule my next blood test?",
        "What questions should I ask my doctor at my next visit?",
    ],
}

def show():
    user = require_auth(["patient"])
    pid  = user["patient_id"]
    lang = user["language"]

    section_header("🧠 AI Health Assistant", "Ask questions about YOUR health records")

    # ── Provider + RAG status banner ──────────────────────────────────────────
    provider = active_provider()
    if provider == "none":
        st.warning(
            "⚠️ No LLM configured. Set **GEMINI_API_KEY** or **OPENAI_API_KEY** in `.env`, "
            "or run **Ollama** locally. The assistant will use rule-based responses only.",
            icon="⚙️",
        )
    else:
        col_a, col_b, col_c = st.columns([2, 2, 1])
        with col_a:
            st.success(f"🤖 **LLM:** {provider_label()}", icon="✅")
        with col_b:
            if RAG_AVAILABLE:
                st.success("🔍 **RAG:** sentence-transformers + FAISS", icon="✅")
            else:
                st.info("🔍 **RAG:** keyword fallback (install faiss-cpu + sentence-transformers)", icon="ℹ️")

    ai_disclaimer(lang)
    st.caption(
        "This assistant reads your medical records — reports, medications, symptoms, "
        "doctor notes — and uses them as context for every answer."
    )

    # ── Build / refresh index ─────────────────────────────────────────────────
    if pid:
        with st.spinner("Loading your health records into memory…"):
            stats = index_stats(pid)

        col1, col2, col3 = st.columns(3)
        src = stats.get("source_counts", {})
        with col1:
            st.metric("📄 Total record chunks", stats["total_chunks"])
        with col2:
            st.metric("🧪 Lab values", src.get("lab_report", 0))
        with col3:
            st.metric("💊 Medications", src.get("medication", 0) + src.get("prescription", 0))

        with st.expander("📊 All indexed sources"):
            labels = {
                "profile": "Patient profile", "lab_report": "Lab report values",
                "symptom": "Symptom logs", "medication": "Active medications",
                "prescription": "Prescription items", "metric": "Health metrics",
                "doctor_note": "Doctor notes",
            }
            for src_key, count in src.items():
                st.markdown(f"- **{labels.get(src_key, src_key)}**: {count} chunks")
            if stats["total_chunks"] == 0:
                st.warning("No records found. Upload reports, log symptoms, or add reminders to enable RAG.")

        col_refresh, _ = st.columns([1, 3])
        with col_refresh:
            if st.button("🔄 Refresh Index", help="Re-index after adding new records"):
                build_patient_index(pid, force=True)
                st.success("Index refreshed.")
                st.rerun()

    st.markdown("---")

    # ── Session chat history ──────────────────────────────────────────────────
    if "rag_chat_history" not in st.session_state:
        st.session_state["rag_chat_history"] = []

    # ── Render existing conversation ──────────────────────────────────────────
    for msg in st.session_state["rag_chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(f"📎 {len(msg['sources'])} record(s) used as context"):
                    for i, src in enumerate(msg["sources"], 1):
                        source_label = src.get("source","").replace("_"," ").title()
                        date_str = f" [{src['date']}]" if src.get("date") and src["date"] != "current" else ""
                        score = src.get("score", 0)
                        st.markdown(
                            f"**[{i}] {source_label}{date_str}** "
                            f"<span style='color:#64748B;font-size:0.8rem'>(relevance: {score:.2f})</span>",
                            unsafe_allow_html=True,
                        )
                        st.caption(src["text"][:200] + ("…" if len(src["text"]) > 200 else ""))

    # ── Suggested questions (shown only when chat is empty) ───────────────────
    if not st.session_state["rag_chat_history"]:
        st.markdown("#### 💡 Suggested questions about your health records")
        for category, questions in SUGGESTIONS.items():
            st.markdown(f"**{category}**")
            cols = st.columns(2)
            for i, q in enumerate(questions):
                with cols[i % 2]:
                    if st.button(q, key=f"sug_{category}_{i}", use_container_width=True):
                        _send(q, pid, lang)
                        st.rerun()
            st.markdown("")

    # ── Chat input ────────────────────────────────────────────────────────────
    user_input = st.chat_input("Ask anything about your health records…")
    if user_input:
        _send(user_input, pid, lang)
        st.rerun()

    # ── Clear button ──────────────────────────────────────────────────────────
    if st.session_state["rag_chat_history"]:
        if st.button("🗑️ Clear conversation", use_container_width=False):
            st.session_state["rag_chat_history"] = []
            st.rerun()


# ── Private helpers ───────────────────────────────────────────────────────────

def _send(message: str, patient_id: int, lang: str):
    """Process one user message: emergency check → RAG retrieve → LLM answer."""

    # Add user message immediately
    st.session_state["rag_chat_history"].append({"role": "user", "content": message})

    # Emergency shortcut — no LLM needed
    if is_emergency(message):
        resp = EMERGENCY_RESPONSE_TA if lang == "ta" else EMERGENCY_RESPONSE_EN
        st.session_state["rag_chat_history"].append({
            "role": "assistant", "content": resp, "sources": [],
        })
        _save_to_db(patient_id, message, resp, lang)
        return

    # Retrieve relevant chunks for transparency display
    sources = []
    if patient_id:
        try:
            sources = retrieve(message, patient_id, k=6)
        except Exception:
            pass

    # Build answer
    try:
        if active_provider() == "none":
            raise RuntimeError("no provider")
        answer = rag_answer(message, patient_id, language=lang)
    except RuntimeError:
        # Graceful degradation: no LLM — show what we retrieved + disclaimer
        from app.core.config import settings
        disclaimer = settings.AI_DISCLAIMER_TA if lang == "ta" else settings.AI_DISCLAIMER_EN
        if sources:
            lines = ["Based on your health records:\n"]
            for s in sources[:3]:
                lines.append(f"• {s['text'][:150]}")
            lines.append(f"\n{disclaimer}")
            answer = "\n".join(lines)
        else:
            answer = (
                "I couldn't find relevant information in your records for this question. "
                "Please consult your doctor for personalised advice.\n\n" + disclaimer
            )
    except Exception as e:
        answer = f"Sorry, an error occurred: {str(e)[:120]}. Please try again."

    st.session_state["rag_chat_history"].append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })
    _save_to_db(patient_id, message, answer, lang)


def _save_to_db(patient_id: int, user_msg: str, assistant_msg: str, lang: str):
    """Persist conversation to chatbot_history table (best effort)."""
    try:
        from app.core.auth import current_user
        from app.core.database import execute_write
        uid = current_user().get("id")
        if not uid:
            return
        execute_write(
            """INSERT INTO chatbot_history
               (user_id, role, message, language, is_ai_response, has_disclaimer, created_at)
               VALUES (:uid, 'user',      :msg, :lang, FALSE, FALSE, NOW())""",
            {"uid": uid, "msg": user_msg, "lang": lang},
        )
        execute_write(
            """INSERT INTO chatbot_history
               (user_id, role, message, language, is_ai_response, has_disclaimer, created_at)
               VALUES (:uid, 'assistant', :msg, :lang, TRUE,  TRUE,  NOW())""",
            {"uid": uid, "msg": assistant_msg[:4000], "lang": lang},
        )
    except Exception:
        pass
