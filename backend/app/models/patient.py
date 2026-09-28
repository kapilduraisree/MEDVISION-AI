from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    date_of_birth = Column(Date)
    gender = Column(String(20))
    blood_group = Column(String(10))
    height_cm = Column(Float)
    weight_kg = Column(Float)
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100), default="India")
    pincode = Column(String(10))
    occupation = Column(String(100))
    marital_status = Column(String(30))
    known_allergies = Column(Text)
    chronic_conditions = Column(Text)
    current_medications = Column(Text)
    family_medical_history = Column(Text)
    insurance_provider = Column(String(200))
    insurance_id = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    user = relationship("User", back_populates="patient")
    family_members = relationship("FamilyMember", back_populates="patient")
    symptoms = relationship("Symptom", back_populates="patient")
    medical_reports = relationship("MedicalReport", back_populates="patient")
    prescriptions = relationship("Prescription", back_populates="patient")
    medication_schedules = relationship("MedicationSchedule", back_populates="patient")
    pharmacy_bills = relationship("PharmacyBill", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")
    health_metrics = relationship("HealthMetric", back_populates="patient")
    emergency_contacts = relationship("EmergencyContact", back_populates="patient")
    documents = relationship("Document", back_populates="patient")


class FamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    name = Column(String(255), nullable=False)
    relation = Column(String(50))          # renamed from 'relationship'
    date_of_birth = Column(Date)
    gender = Column(String(20))
    blood_group = Column(String(10))
    known_allergies = Column(Text)
    chronic_conditions = Column(Text)
    current_medications = Column(Text)
    profile_image = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    patient = relationship("Patient", back_populates="family_members")
    symptoms = relationship("Symptom", back_populates="family_member")
    medical_reports = relationship("MedicalReport", back_populates="family_member")
    prescriptions = relationship("Prescription", back_populates="family_member")
    medication_schedules = relationship("MedicationSchedule", back_populates="family_member")
    appointments = relationship("Appointment", back_populates="family_member")
    documents = relationship("Document", back_populates="family_member")
