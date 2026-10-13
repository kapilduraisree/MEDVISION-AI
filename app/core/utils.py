"""
MedVision AI – Shared UI Utilities
Reusable Streamlit helpers used across all pages.
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import streamlit as st

from app.core.config import settings


# ── File upload helper ────────────────────────────────────────────────────────
def save_uploaded_file(uploaded_file, subfolder: str = "general") -> Optional[str]:
    """
    Save a Streamlit UploadedFile to disk.
    Returns the file path string, or None on failure.
    """
    if uploaded_file is None:
        return None
    try:
        folder = Path(settings.UPLOAD_DIR) / subfolder
        folder.mkdir(parents=True, exist_ok=True)
        ext = Path(uploaded_file.name).suffix
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = folder / filename
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return str(filepath)
    except Exception as e:
        st.error(f"File save failed: {e}")
        return None


# ── Status badge renderer ─────────────────────────────────────────────────────
def status_badge(status: str) -> str:
    """Return a coloured emoji + text label for a status string."""
    mapping = {
        "normal": "🟢 Normal",
        "attention": "🟡 Attention",
        "abnormal": "🔴 Abnormal",
        "unknown": "⚪ Unknown",
        "pending": "🟡 Pending",
        "confirmed": "🟢 Confirmed",
        "cancelled": "🔴 Cancelled",
        "completed": "✅ Completed",
        "requested": "📋 Requested",
        "taken": "✅ Taken",
        "missed": "❌ Missed",
    }
    return mapping.get(status.lower(), f"• {status.capitalize()}")


# ── Metric card ───────────────────────────────────────────────────────────────
def metric_card(label: str, value: str, delta: str = "", color: str = "#0EA5E9"):
    st.markdown(
        f"""
        <div style="
            background: #1E293B;
            border-left: 4px solid {color};
            border-radius: 8px;
            padding: 14px 18px;
            margin-bottom: 8px;
        ">
            <div style="font-size: 0.78rem; color: #94A3B8; text-transform: uppercase;
                        letter-spacing: 0.05em;">{label}</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: #F1F5F9;
                        margin: 4px 0;">{value}</div>
            {f'<div style="font-size: 0.8rem; color: #64748B;">{delta}</div>' if delta else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Section header ────────────────────────────────────────────────────────────
def section_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div style="margin-bottom: 1.2rem;">
            <h2 style="color: #F1F5F9; margin-bottom: 2px;">{title}</h2>
            {f'<p style="color: #94A3B8; margin: 0;">{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Disclaimer box ────────────────────────────────────────────────────────────
def ai_disclaimer(language: str = "en"):
    text = (
        settings.AI_DISCLAIMER_TA if language == "ta"
        else settings.AI_DISCLAIMER_EN
    )
    st.warning(text)


# ── Emergency alert ───────────────────────────────────────────────────────────
def emergency_alert():
    st.error(
        "🚨 **EMERGENCY**: If you or someone is in immediate danger, "
        "call **112** (India) or your local emergency number immediately. "
        "This app cannot provide emergency medical care."
    )


# ── Date formatting ───────────────────────────────────────────────────────────
def fmt_date(dt) -> str:
    if dt is None:
        return "—"
    if isinstance(dt, str):
        return dt[:10]
    return dt.strftime("%d %b %Y")


def fmt_datetime(dt) -> str:
    if dt is None:
        return "—"
    if isinstance(dt, str):
        return dt[:16].replace("T", " ")
    return dt.strftime("%d %b %Y, %H:%M")


# ── Page not found ────────────────────────────────────────────────────────────
def page_not_found():
    st.error("404 – Page not found.")
