from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    family_member_id = Column(Integer, ForeignKey("family_members.id"), nullable=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    file_path = Column(String(500))
    original_filename = Column(String(500))
    ocr_raw_text = Column(Text)
    ocr_confidence = Column(Float)
    prescription_date = Column(DateTime)
    is_user_verified = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    patient = relationship("Patient", back_populates="prescriptions")
    family_member = relationship("FamilyMember", back_populates="prescriptions")
    doctor = relationship("Doctor", back_populates="prescriptions")
    items = relationship("PrescriptionItem", back_populates="prescription", cascade="all, delete-orphan")


class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False)
    medicine_name = Column(String(300))
    strength = Column(String(100))
    dosage_instruction = Column(String(300))
    frequency = Column(String(100))
    duration = Column(String(100))
    before_after_food = Column(String(50))
    doctor_notes = Column(Text)
    ocr_confidence = Column(Float)
    needs_verification = Column(Boolean, default=False)
    is_user_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    prescription = relationship("Prescription", back_populates="items")
