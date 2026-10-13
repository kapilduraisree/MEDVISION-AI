"""
MedVision AI – RAG Engine
Retrieval-Augmented Generation over a patient's own health records.

Architecture:
  1. build_patient_index(patient_id)  → loads all DB records → chunks → embeds → FAISS index
  2. retrieve(query, patient_id, k)   → embed query → similarity search → top-k chunks
  3. build_rag_context(query, pid)    → retrieve + format as LLM context string
  4. rag_answer(query, pid, system)   → retrieve + inject into LLM → answer string

Embedding model: sentence-transformers/all-MiniLM-L6-v2 (local, ~80 MB, no API key)
Vector store:    FAISS IndexFlatL2 (in-memory, cached per patient in st.session_state)
Fallback:        If sentence-transformers / FAISS not installed, returns plain DB text
"""
from __future__ import annotations
import hashlib
import json
from typing import Optional
from datetime import datetime

import streamlit as st

from app.core.database import execute_query
from app.core.config import settings

# ── Dependency guards ─────────────────────────────────────────────────────────
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import faiss
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

# ── Embedding model (loaded once per process) ─────────────────────────────────
_EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

@st.cache_resource(show_spinner=False)
def _load_embed_model():
    if not RAG_AVAILABLE:
        return None
    return SentenceTransformer(_EMBED_MODEL_NAME)


# ── Document chunk helpers ────────────────────────────────────────────────────

def _chunks_from_patient(patient_id: int) -> list[dict]:
    """
    Pull all relevant patient data from DB and convert to text chunks.
    Each chunk = {"text": str, "source": str, "date": str}
    """
    chunks = []

    # 1. Patient profile
    try:
        rows = execute_query(
            """SELECT p.date_of_birth, p.gender, p.blood_group, p.height_cm, p.weight_kg,
                      p.known_allergies, p.chronic_conditions, p.current_medications,
                      p.family_medical_history, u.full_name
               FROM patients p JOIN users u ON p.user_id = u.id
               WHERE p.id = :pid""",
            {"pid": patient_id},
        )
        if rows:
            r = rows[0]
            dob = str(r[0]) if r[0] else "unknown"
            text = (
                f"Patient: {r[9]}. Gender: {r[1] or 'N/A'}. Blood group: {r[2] or 'N/A'}. "
                f"DOB: {dob}. Height: {r[3] or 'N/A'} cm. Weight: {r[4] or 'N/A'} kg. "
                f"Known allergies: {r[5] or 'none'}. "
                f"Chronic conditions: {r[6] or 'none'}. "
                f"Current medications: {r[7] or 'none'}. "
                f"Family history: {r[8] or 'none'}."
            )
            chunks.append({"text": text, "source": "profile", "date": "current"})
    except Exception:
        pass

    # 2. Lab report values (most recent 50)
    try:
        rows = execute_query(
            """SELECT rv.test_name, rv.result, rv.unit, rv.reference_range_text,
                      rv.status, rv.explanation, mr.report_date, mr.report_type, mr.lab_name
               FROM report_values rv
               JOIN medical_reports mr ON rv.report_id = mr.id
               WHERE mr.patient_id = :pid
               ORDER BY mr.report_date DESC NULLS LAST
               LIMIT 60""",
            {"pid": patient_id},
        )
        for r in rows:
            status_word = r[4] or "unknown"
            text = (
                f"Lab result ({r[7] or 'report'} from {r[8] or 'lab'} on {str(r[6])[:10]}): "
                f"{r[0]} = {r[1]} {r[2] or ''}. Reference range: {r[3] or 'N/A'}. "
                f"Status: {status_word}. "
                + (f"Explanation: {r[5][:200]}" if r[5] else "")
            )
            chunks.append({"text": text, "source": "lab_report", "date": str(r[6])[:10]})
    except Exception:
        pass

    # 3. Symptoms (most recent 30)
    try:
        rows = execute_query(
            """SELECT description, severity, duration, location_on_body, created_at
               FROM symptoms WHERE patient_id = :pid
               ORDER BY created_at DESC LIMIT 30""",
            {"pid": patient_id},
        )
        for r in rows:
            text = (
                f"Symptom logged on {str(r[4])[:10]}: {r[0]}. "
                f"Severity: {r[1] or 'N/A'}. Duration: {r[2] or 'N/A'}. "
                f"Location: {r[3] or 'N/A'}."
            )
            chunks.append({"text": text, "source": "symptom", "date": str(r[4])[:10]})
    except Exception:
        pass

    # 4. Active medications / reminders
    try:
        rows = execute_query(
            """SELECT medicine_name, strength, frequency, times, before_after_food,
                      instructions, start_date
               FROM medication_schedules
               WHERE patient_id = :pid AND is_active = TRUE""",
            {"pid": patient_id},
        )
        for r in rows:
            text = (
                f"Active medication: {r[0]} {r[1] or ''}. Frequency: {r[2] or 'N/A'}. "
                f"Times: {r[3] or 'N/A'}. Food instruction: {r[4] or 'N/A'}. "
                f"Instructions: {r[5] or 'none'}. Started: {str(r[6])[:10]}."
            )
            chunks.append({"text": text, "source": "medication", "date": str(r[6])[:10]})
    except Exception:
        pass

    # 5. Prescriptions (extracted medicines)
    try:
        rows = execute_query(
            """SELECT pi.medicine_name, pi.strength, pi.dosage_instruction,
                      pi.frequency, p.created_at
               FROM prescription_items pi
               JOIN prescriptions p ON pi.prescription_id = p.id
               WHERE p.patient_id = :pid
               ORDER BY p.created_at DESC LIMIT 30""",
            {"pid": patient_id},
        )
        for r in rows:
            text = (
                f"Prescribed medicine ({str(r[4])[:10]}): {r[0]} {r[1] or ''}. "
                f"Dosage: {r[2] or 'N/A'}. Frequency: {r[3] or 'N/A'}."
            )
            chunks.append({"text": text, "source": "prescription", "date": str(r[4])[:10]})
    except Exception:
        pass

    # 6. Health metrics (most recent 40)
    try:
        rows = execute_query(
            """SELECT metric_name, value, unit, recorded_date, notes
               FROM health_metrics WHERE patient_id = :pid
               ORDER BY recorded_date DESC LIMIT 40""",
            {"pid": patient_id},
        )
        for r in rows:
            text = (
                f"Health metric on {str(r[3])[:10]}: {r[0]} = {r[1]} {r[2] or ''}."
                + (f" Note: {r[4]}" if r[4] else "")
            )
            chunks.append({"text": text, "source": "metric", "date": str(r[3])[:10]})
    except Exception:
        pass

    # 7. Doctor notes
    try:
        rows = execute_query(
            """SELECT dn.note_text, dn.follow_up_date, dn.created_at, u.full_name
               FROM doctor_notes dn
               JOIN doctors d ON dn.doctor_id = d.id
               JOIN users u ON d.user_id = u.id
               WHERE dn.patient_id = :pid
               ORDER BY dn.created_at DESC LIMIT 20""",
            {"pid": patient_id},
        )
        for r in rows:
            text = (
                f"Doctor note by Dr. {r[3]} on {str(r[2])[:10]}: {r[0][:400]}."
                + (f" Follow-up: {str(r[1])[:10]}" if r[1] else "")
            )
            chunks.append({"text": text, "source": "doctor_note", "date": str(r[2])[:10]})
    except Exception:
        pass

    return chunks


# ── Index management ──────────────────────────────────────────────────────────

def _index_cache_key(patient_id: int) -> str:
    return f"rag_index_{patient_id}"


def _chunks_hash(chunks: list[dict]) -> str:
    raw = json.dumps([c["text"] for c in chunks], sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def build_patient_index(patient_id: int, force: bool = False) -> dict:
    """
    Build (or return cached) FAISS index for a patient.
    Returns {"index": faiss.Index, "chunks": list, "hash": str, "count": int}
    Returns {"index": None, "chunks": list, "hash": "", "count": len}  if RAG unavailable.
    """
    cache_key = _index_cache_key(patient_id)
    chunks = _chunks_from_patient(patient_id)

    if not chunks:
        return {"index": None, "chunks": [], "hash": "", "count": 0}

    new_hash = _chunks_hash(chunks)

    # Return cached index if data hasn't changed
    cached = st.session_state.get(cache_key)
    if cached and cached.get("hash") == new_hash and not force:
        return cached

    if not RAG_AVAILABLE:
        result = {"index": None, "chunks": chunks, "hash": new_hash, "count": len(chunks)}
        st.session_state[cache_key] = result
        return result

    # Build embeddings + FAISS index
    model = _load_embed_model()
    if model is None:
        result = {"index": None, "chunks": chunks, "hash": new_hash, "count": len(chunks)}
        st.session_state[cache_key] = result
        return result

    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype="float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)   # Inner product (= cosine on normalized vectors)
    index.add(embeddings)

    result = {"index": index, "chunks": chunks, "hash": new_hash, "count": len(chunks)}
    st.session_state[cache_key] = result
    return result


# ── Retrieval ─────────────────────────────────────────────────────────────────

def retrieve(query: str, patient_id: int, k: int = 6) -> list[dict]:
    """
    Return the top-k most relevant chunks for a query.
    Each item: {"text": str, "source": str, "date": str, "score": float}
    Falls back to first-k chunks if RAG is unavailable.
    """
    idx_data = build_patient_index(patient_id)
    chunks = idx_data["chunks"]

    if not chunks:
        return []

    if not RAG_AVAILABLE or idx_data["index"] is None:
        # Fallback: keyword match
        query_lower = query.lower()
        scored = []
        for c in chunks:
            score = sum(1 for word in query_lower.split() if word in c["text"].lower())
            scored.append({**c, "score": score})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:k]

    model = _load_embed_model()
    q_emb = model.encode([query], normalize_embeddings=True)
    q_emb = np.array(q_emb, dtype="float32")

    k_actual = min(k, idx_data["index"].ntotal)
    scores, indices = idx_data["index"].search(q_emb, k_actual)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        results.append({**chunks[idx], "score": float(score)})
    return results


def build_rag_context(query: str, patient_id: int, k: int = 6) -> str:
    """
    Retrieve top-k chunks and format as a structured context block for the LLM.
    """
    hits = retrieve(query, patient_id, k=k)
    if not hits:
        return ""

    SOURCE_LABELS = {
        "profile":      "Patient Profile",
        "lab_report":   "Lab Report",
        "symptom":      "Symptom Log",
        "medication":   "Active Medication",
        "prescription": "Prescription",
        "metric":       "Health Metric",
        "doctor_note":  "Doctor Note",
    }

    lines = ["=== PATIENT HEALTH RECORDS (retrieved for this query) ==="]
    for i, hit in enumerate(hits, 1):
        label = SOURCE_LABELS.get(hit["source"], hit["source"].replace("_", " ").title())
        date_str = f" [{hit['date']}]" if hit.get("date") and hit["date"] != "current" else ""
        lines.append(f"[{i}] {label}{date_str}: {hit['text']}")
    lines.append("=== END OF PATIENT RECORDS ===")
    return "\n".join(lines)


def rag_answer(
    query: str,
    patient_id: int,
    system_extra: str = "",
    language: str = "en",
    k: int = 6,
) -> str:
    """
    Full RAG pipeline: retrieve relevant records → inject as context → LLM answer.
    Returns the LLM answer string, or raises RuntimeError if no LLM available.
    """
    from app.services.ai.llm_client import llm_chat

    context = build_rag_context(query, patient_id, k=k)

    system_base = (
        "You are MedVision AI, a medical information assistant helping a patient "
        "understand their own health records.\n\n"
        "STRICT RULES:\n"
        "1. Base your answer on the provided patient records when relevant.\n"
        "2. Never diagnose medical conditions.\n"
        "3. Never prescribe or recommend changing medications.\n"
        "4. For emergencies, direct the patient to call 112 immediately.\n"
        "5. Always end with the disclaimer: "
        "'⚠️ This is informational only. Consult your doctor for medical decisions.'\n"
        "6. If the patient records do not contain information relevant to the question, "
        "say so clearly and answer from general medical knowledge.\n"
    )
    if language == "ta":
        system_base += "\nRespond in Tamil (தமிழ்).\n"

    if system_extra:
        system_base += f"\n{system_extra}"

    user_content = f"{context}\n\nPatient question: {query}" if context else query

    messages = [{"role": "user", "content": user_content}]
    return llm_chat(messages, system=system_base, max_tokens=700, temperature=0.3,
                    language=language)


def index_stats(patient_id: int) -> dict:
    """Return stats about the patient's RAG index for display in the UI."""
    idx_data = build_patient_index(patient_id)
    chunks = idx_data.get("chunks", [])
    source_counts: dict[str, int] = {}
    for c in chunks:
        src = c.get("source", "other")
        source_counts[src] = source_counts.get(src, 0) + 1
    return {
        "total_chunks": len(chunks),
        "rag_available": RAG_AVAILABLE,
        "source_counts": source_counts,
        "index_built": idx_data.get("index") is not None,
    }
