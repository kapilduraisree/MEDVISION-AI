from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Symptom(Base):
    __tablename__ = "symptoms"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    family_member_id = Column(Integer, ForeignKey("family_members.id"), nullable=True)
    description = Column(Text, nullable=False)
    input_method = Column(String(20), default="text")
    voice_transcript = Column(Text)
    duration = Column(String(100))
    severity = Column(String(20))
    location_on_body = Column(String(200))
    language = Column(String(10), default="en")
    is_emergency_flagged = Column(Boolean, default=False)
    emergency_reason = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    patient = relationship("Patient", back_populates="symptoms")
    family_member = relationship("FamilyMember", back_populates="symptoms")
