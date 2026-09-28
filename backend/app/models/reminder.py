from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class MedicationSchedule(Base):
    __tablename__ = "medication_schedules"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    family_member_id = Column(Integer, ForeignKey("family_members.id"), nullable=True)
    medicine_name = Column(String(300), nullable=False)
    strength = Column(String(100))
    frequency = Column(String(100))
    times = Column(String(500))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    instructions = Column(Text)
    before_after_food = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    patient = relationship("Patient", back_populates="medication_schedules")
    family_member = relationship("FamilyMember", back_populates="medication_schedules")
    logs = relationship("MedicationLog", back_populates="schedule", cascade="all, delete-orphan")


class MedicationLog(Base):
    __tablename__ = "medication_logs"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("medication_schedules.id"), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(String(20), default="pending")
    taken_at = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    schedule = relationship("MedicationSchedule", back_populates="logs")
