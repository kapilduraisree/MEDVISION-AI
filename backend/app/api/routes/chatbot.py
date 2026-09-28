from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.chatbot import ChatbotHistory
from app.services.ai.chatbot_service import get_chatbot_response
import uuid

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    session_id: Optional[str] = None
    input_method: str = "text"  # text, voice


@router.post("/message")
def send_message(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not data.session_id:
        data.session_id = uuid.uuid4().hex

    # Get conversation history for context
    history = (
        db.query(ChatbotHistory)
        .filter(
            ChatbotHistory.user_id == current_user.id,
            ChatbotHistory.session_id == data.session_id,
        )
        .order_by(ChatbotHistory.created_at.desc())
        .limit(6)
        .all()
    )
    history_list = [{"role": h.role, "message": h.message} for h in reversed(history)]

    # Get AI response
    result = get_chatbot_response(data.message, data.language, history_list)

    # Save user message
    db.add(ChatbotHistory(
        user_id=current_user.id,
        session_id=data.session_id,
        role="user",
        message=data.message,
        language=data.language,
        input_method=data.input_method,
        is_ai_response=False,
    ))

    # Save assistant response
    db.add(ChatbotHistory(
        user_id=current_user.id,
        session_id=data.session_id,
        role="assistant",
        message=result["response"],
        language=data.language,
        is_ai_response=True,
        has_disclaimer=result.get("has_disclaimer", True),
    ))

    db.commit()

    return {
        "session_id": data.session_id,
        "response": result["response"],
        "is_emergency": result.get("is_emergency", False),
        "has_disclaimer": result.get("has_disclaimer", True),
        "disclaimer": (
            "⚠️ AI-generated information. Not a substitute for professional medical advice."
        ),
    }


@router.get("/history")
def get_chat_history(
    session_id: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(ChatbotHistory).filter(
        ChatbotHistory.user_id == current_user.id
    )
    if session_id:
        query = query.filter(ChatbotHistory.session_id == session_id)

    messages = query.order_by(ChatbotHistory.created_at.asc()).limit(limit).all()

    return {
        "messages": [
            {
                "id": m.id,
                "session_id": m.session_id,
                "role": m.role,
                "message": m.message,
                "language": m.language,
                "created_at": m.created_at,
            }
            for m in messages
        ]
    }


@router.get("/sessions")
def get_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of unique chat sessions."""
    from sqlalchemy import distinct, func
    sessions = (
        db.query(
            ChatbotHistory.session_id,
            func.count(ChatbotHistory.id).label("message_count"),
            func.max(ChatbotHistory.created_at).label("last_message"),
        )
        .filter(ChatbotHistory.user_id == current_user.id)
        .group_by(ChatbotHistory.session_id)
        .order_by(func.max(ChatbotHistory.created_at).desc())
        .limit(20)
        .all()
    )

    return {
        "sessions": [
            {
                "session_id": s.session_id,
                "message_count": s.message_count,
                "last_message": s.last_message,
            }
            for s in sessions
        ]
    }
