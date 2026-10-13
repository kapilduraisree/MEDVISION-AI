"""
MedVision AI – Authentication & Session Management
Handles password hashing, login verification, and Streamlit session state.
"""
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

import streamlit as st

from app.core.database import execute_query, execute_write
from app.core.config import settings


# ── Password hashing (bcrypt-style using hashlib for no extra dep) ────────────
def _hash_password(password: str) -> str:
    """Hash password with SHA-256 + random salt."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}{settings.SECRET_KEY}".encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(plain: str, hashed_stored: str) -> bool:
    """Verify a plain password against a stored hash."""
    # Support legacy bcrypt hashes from old FastAPI backend
    if hashed_stored.startswith("$2b$") or hashed_stored.startswith("$2a$"):
        try:
            import bcrypt
            return bcrypt.checkpw(plain.encode(), hashed_stored.encode())
        except Exception:
            return False

    # Our own salt:hash format
    if ":" not in hashed_stored:
        return False
    salt, hashed = hashed_stored.split(":", 1)
    expected = hashlib.sha256(f"{salt}{plain}{settings.SECRET_KEY}".encode()).hexdigest()
    return hmac.compare_digest(expected, hashed)


def hash_password(password: str) -> str:
    return _hash_password(password)


# ── User lookup ───────────────────────────────────────────────────────────────
def get_user_by_email(email: str) -> Optional[dict]:
    rows = execute_query(
        "SELECT id, email, full_name, hashed_password, role, is_active, preferred_language "
        "FROM users WHERE email = :email",
        {"email": email.lower().strip()},
    )
    if not rows:
        return None
    r = rows[0]
    return {
        "id": r[0], "email": r[1], "full_name": r[2],
        "hashed_password": r[3], "role": r[4],
        "is_active": r[5], "preferred_language": r[6],
    }


def get_patient_id(user_id: int) -> Optional[int]:
    rows = execute_query(
        "SELECT id FROM patients WHERE user_id = :uid", {"uid": user_id}
    )
    return rows[0][0] if rows else None


def get_doctor_id(user_id: int) -> Optional[int]:
    rows = execute_query(
        "SELECT id FROM doctors WHERE user_id = :uid", {"uid": user_id}
    )
    return rows[0][0] if rows else None


# ── Login / Register ──────────────────────────────────────────────────────────
def login(email: str, password: str) -> tuple[bool, str]:
    """
    Attempt login. Returns (success, message).
    On success, populates st.session_state with user info.
    """
    user = get_user_by_email(email)
    if not user:
        return False, "No account found with that email."
    if not user["is_active"]:
        return False, "This account has been deactivated. Contact support."
    if not verify_password(password, user["hashed_password"]):
        return False, "Incorrect password."

    # Update last_login
    execute_write(
        "UPDATE users SET last_login = NOW() WHERE id = :uid", {"uid": user["id"]}
    )

    # Populate session state
    st.session_state["authenticated"] = True
    st.session_state["user_id"] = user["id"]
    st.session_state["user_email"] = user["email"]
    st.session_state["user_name"] = user["full_name"]
    st.session_state["user_role"] = user["role"]
    st.session_state["language"] = user["preferred_language"] or "en"

    # Role-specific IDs
    if user["role"] == "patient":
        st.session_state["patient_id"] = get_patient_id(user["id"])
    elif user["role"] == "doctor":
        st.session_state["doctor_id"] = get_doctor_id(user["id"])

    return True, "Login successful."


def register_user(email: str, full_name: str, phone: str,
                  password: str, role: str = "patient") -> tuple[bool, str]:
    """Register a new user. Returns (success, message)."""
    if get_user_by_email(email):
        return False, "An account with this email already exists."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    hashed = hash_password(password)
    try:
        execute_write(
            """INSERT INTO users (email, full_name, phone, hashed_password, role, is_active, is_verified, created_at)
               VALUES (:email, :name, :phone, :pwd, :role, TRUE, FALSE, NOW())""",
            {"email": email.lower().strip(), "name": full_name.strip(),
             "phone": phone.strip(), "pwd": hashed, "role": role},
        )
        # Create patient / doctor profile row
        rows = execute_query(
            "SELECT id FROM users WHERE email = :email",
            {"email": email.lower().strip()},
        )
        if rows:
            uid = rows[0][0]
            if role == "patient":
                execute_write(
                    "INSERT INTO patients (user_id, created_at) VALUES (:uid, NOW())",
                    {"uid": uid},
                )
            elif role == "doctor":
                execute_write(
                    "INSERT INTO doctors (user_id, created_at) VALUES (:uid, NOW())",
                    {"uid": uid},
                )
        return True, "Account created successfully. Please log in."
    except Exception as e:
        return False, f"Registration failed: {str(e)}"


# ── Session helpers ───────────────────────────────────────────────────────────
def logout():
    keys = [
        "authenticated", "user_id", "user_email", "user_name",
        "user_role", "language", "patient_id", "doctor_id", "active_page",
    ]
    for k in keys:
        st.session_state.pop(k, None)


def is_authenticated() -> bool:
    return st.session_state.get("authenticated", False)


def current_user() -> dict:
    return {
        "id": st.session_state.get("user_id"),
        "name": st.session_state.get("user_name", ""),
        "email": st.session_state.get("user_email", ""),
        "role": st.session_state.get("user_role", "patient"),
        "language": st.session_state.get("language", "en"),
        "patient_id": st.session_state.get("patient_id"),
        "doctor_id": st.session_state.get("doctor_id"),
    }


def require_auth(allowed_roles: list = None):
    """
    Call at top of every page function.
    Redirects to login if not authenticated.
    Returns current_user() dict on success.
    """
    if not is_authenticated():
        st.session_state["active_page"] = "login"
        st.rerun()
    user = current_user()
    if allowed_roles and user["role"] not in allowed_roles:
        st.error("🚫 You don't have permission to view this page.")
        st.stop()
    return user
