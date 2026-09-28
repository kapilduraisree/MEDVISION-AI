from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ChatbotHistory(Base):
    __tablename__ = "chatbot_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(100))
    role = Column(String(20))
    message = Column(Text, nullable=False)
    language = Column(String(10), default="en")
    input_method = Column(String(20), default="text")
    is_ai_response = Column(Boolean, default=False)
    ai_confidence = Column(Float)
    has_disclaimer = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="chatbot_history")
