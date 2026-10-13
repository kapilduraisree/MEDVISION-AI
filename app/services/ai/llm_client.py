"""
MedVision AI – Unified LLM Client
Priority order: Google Gemini 1.5 Flash → OpenAI GPT-4o → Ollama (local) → rule-based fallback.

Usage:
    from app.services.ai.llm_client import llm_complete, llm_chat, active_provider

    response = llm_complete(prompt="Explain HbA1c in simple terms")
    response = llm_chat(messages=[...], system="You are a medical assistant")
    provider = active_provider()   # "gemini" | "openai" | "ollama" | "none"
"""
from __future__ import annotations
import os
from typing import Optional
from app.core.config import settings

# ── Provider detection ────────────────────────────────────────────────────────

def active_provider() -> str:
    """Return the name of the first available LLM provider."""
    if settings.GEMINI_API_KEY:
        return "gemini"
    if settings.OPENAI_API_KEY:
        return "openai"
    if _ollama_available():
        return "ollama"
    return "none"


def _ollama_available() -> bool:
    try:
        import httpx
        r = httpx.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=2.0)
        return r.status_code == 200
    except Exception:
        return False


# ── Public interface ──────────────────────────────────────────────────────────

def llm_complete(
    prompt: str,
    system: str = "",
    max_tokens: int = 800,
    temperature: float = 0.4,
    language: str = "en",
) -> str:
    """
    Send a single prompt to the best available LLM.
    Returns the text response string.
    Raises RuntimeError if no provider is available.
    """
    messages = [{"role": "user", "content": prompt}]
    return llm_chat(messages, system=system, max_tokens=max_tokens,
                    temperature=temperature, language=language)


def llm_chat(
    messages: list[dict],
    system: str = "",
    max_tokens: int = 800,
    temperature: float = 0.4,
    language: str = "en",
) -> str:
    """
    Send a chat-style messages list to the best available LLM.
    messages format: [{"role": "user"|"assistant", "content": "..."}]
    Returns the assistant text response.
    """
    provider = active_provider()

    if provider == "gemini":
        return _gemini_chat(messages, system, max_tokens, temperature)
    if provider == "openai":
        return _openai_chat(messages, system, max_tokens, temperature)
    if provider == "ollama":
        return _ollama_chat(messages, system, max_tokens, temperature)

    raise RuntimeError(
        "No LLM provider configured. Set GEMINI_API_KEY or OPENAI_API_KEY in .env, "
        "or run Ollama locally."
    )


def provider_label() -> str:
    """Human-readable label for the active provider."""
    labels = {
        "gemini": "Google Gemini 1.5 Flash",
        "openai": f"OpenAI {settings.OPENAI_MODEL}",
        "ollama": f"Ollama ({settings.OLLAMA_MODEL})",
        "none":   "Rule-based fallback (no LLM configured)",
    }
    return labels.get(active_provider(), "Unknown")


# ── Gemini ────────────────────────────────────────────────────────────────────

def _gemini_chat(messages: list[dict], system: str,
                 max_tokens: int, temperature: float) -> str:
    import google.generativeai as genai

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name=settings.GEMINI_MODEL,
        system_instruction=system or None,
        generation_config=genai.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        ),
    )

    # Convert OpenAI-style messages to Gemini history format
    history = []
    last_user = ""
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        if m["role"] == "user":
            last_user = m["content"]
        history.append({"role": role, "parts": [m["content"]]})

    # Gemini needs history without the final user turn
    chat = model.start_chat(history=history[:-1] if len(history) > 1 else [])
    response = chat.send_message(last_user or messages[-1]["content"])
    return response.text


# ── OpenAI ────────────────────────────────────────────────────────────────────

def _openai_chat(messages: list[dict], system: str,
                 max_tokens: int, temperature: float) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=full_messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content


# ── Ollama ────────────────────────────────────────────────────────────────────

def _ollama_chat(messages: list[dict], system: str,
                 max_tokens: int, temperature: float) -> str:
    import httpx, json

    payload = {
        "model": settings.OLLAMA_MODEL,
        "messages": messages,
        "system": system,
        "stream": False,
        "options": {"num_predict": max_tokens, "temperature": temperature},
    }
    r = httpx.post(
        f"{settings.OLLAMA_BASE_URL}/api/chat",
        json=payload,
        timeout=120.0,
    )
    r.raise_for_status()
    return r.json()["message"]["content"]
