from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class MedicalReport(Base):
    __tablename__ = "medical_reports"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    family_member_id = Column(Integer, ForeignKey("family_members.id"), nullable=True)
    report_type = Column(String(100))
    report_date = Column(DateTime)
    lab_name = Column(String(300))
    doctor_name = Column(String(300))
    file_path = Column(String(500))
    file_type = Column(String(20))
    original_filename = Column(String(500))
    ocr_raw_text = Column(Text)
    ocr_confidence = Column(Float)
    is_ocr_verified = Column(Boolean, default=False)
    ai_explanation = Column(Text)
    ai_explanation_tamil = Column(Text)
    ai_questions_for_doctor = Column(Text)
    summary = Column(Text)
    is_doctor_reviewed = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    patient = relationship("Patient", back_populates="medical_reports")
    family_member = relationship("FamilyMember", back_populates="medical_reports")
    report_values = relationship("ReportValue", back_populates="report", cascade="all, delete-orphan")


class ReportValue(Base):
    __tablename__ = "report_values"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("medical_reports.id"), nullable=False)
    test_name = Column(String(300), nullable=False)
    result = Column(String(100))
    unit = Column(String(50))
    reference_range_low = Column(Float)
    reference_range_high = Column(Float)
    reference_range_text = Column(String(200))
    status = Column(String(20))
    explanation = Column(Text)
    explanation_tamil = Column(Text)
    is_manually_corrected = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    report = relationship("MedicalReport", back_populates="report_values")
