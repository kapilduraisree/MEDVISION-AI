"""
MedVision AI – Configuration (v2)
Reads from environment variables / .env file.
New in v2: LLM model selection, Ollama settings, RAG toggles.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    # ── App ───────────────────────────────────────────────────────────────────
    APP_TITLE: str   = os.getenv("APP_TITLE",   "MedVision AI")
    APP_VERSION: str = os.getenv("APP_VERSION", "2.1.0")

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://medvision:medvision_secret@localhost:5432/medvision_ai",
    )

    # ── Security ──────────────────────────────────────────────────────────────
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "medvision-default-secret-key-change-in-production-32ch"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

    # ── LLM — Google Gemini (highest priority) ────────────────────────────────
    GEMINI_API_KEY: str  = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str    = os.getenv("GEMINI_MODEL",   "gemini-1.5-flash")

    # ── LLM — OpenAI (second priority) ───────────────────────────────────────
    OPENAI_API_KEY: str  = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str    = os.getenv("OPENAI_MODEL",   "gpt-4o-mini")

    # ── LLM — Ollama local (third priority) ──────────────────────────────────
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str    = os.getenv("OLLAMA_MODEL",    "llama3.2")

    # ── RAG settings ──────────────────────────────────────────────────────────
    RAG_ENABLED: bool    = os.getenv("RAG_ENABLED", "true").lower() == "true"
    RAG_TOP_K: int       = int(os.getenv("RAG_TOP_K", "6"))
    # Embedding model downloaded on first use (~80 MB, cached by sentence-transformers)
    RAG_EMBED_MODEL: str = os.getenv(
        "RAG_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )

    # ── File uploads ──────────────────────────────────────────────────────────
    UPLOAD_DIR: str            = os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads"))
    ALLOWED_IMAGE_TYPES: list  = ["jpg", "jpeg", "png", "bmp", "tiff", "webp"]
    ALLOWED_DOC_TYPES: list    = ["pdf", "docx", "doc", "jpg", "jpeg", "png"]
    MAX_UPLOAD_MB: int         = 50

    # ── Medical AI disclaimers ────────────────────────────────────────────────
    AI_DISCLAIMER_EN: str = (
        "⚠️ This information is for educational purposes only and does not constitute "
        "medical advice or diagnosis. Always consult a qualified healthcare professional."
    )
    AI_DISCLAIMER_TA: str = (
        "⚠️ இந்த தகவல் கல்வி நோக்கங்களுக்காக மட்டுமே. இது மருத்துவ ஆலோசனை அல்ல. "
        "தகுதி வாய்ந்த மருத்துவரை அணுகவும்."
    )


settings = Settings()
