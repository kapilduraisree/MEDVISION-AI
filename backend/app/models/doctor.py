from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    specialization = Column(String(200))
    qualification = Column(String(500))
    registration_number = Column(String(100), unique=True)
    hospital_name = Column(String(300))
    hospital_address = Column(Text)
    city = Column(String(100))
    years_of_experience = Column(Integer, default=0)
    consultation_fee = Column(Float, default=0)
    available_days = Column(String(500))
    available_time_start = Column(String(10))
    available_time_end = Column(String(10))
    bio = Column(Text)
    is_verified = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    user = relationship("User", back_populates="doctor")
    notes = relationship("DoctorNote", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")
    prescriptions = relationship("Prescription", back_populates="doctor")


class DoctorNote(Base):
    __tablename__ = "doctor_notes"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    report_id = Column(Integer, ForeignKey("medical_reports.id"), nullable=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    note_text = Column(Text, nullable=False)
    follow_up_date = Column(DateTime)
    is_approved_summary = Column(Boolean, default=False)
    approved_summary_text = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    doctor = relationship("Doctor", back_populates="notes")
