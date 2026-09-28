from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    family_member_id = Column(Integer, ForeignKey("family_members.id"), nullable=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    reason = Column(Text)
    status = Column(String(30), default="requested")
    notes = Column(Text)
    follow_up_date = Column(DateTime)
    is_reminder_sent = Column(Boolean, default=False)
    patient_rating = Column(Integer)
    patient_feedback = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    patient = relationship("Patient", back_populates="appointments")
    family_member = relationship("FamilyMember", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
