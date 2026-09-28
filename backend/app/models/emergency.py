from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    name = Column(String(255), nullable=False)
    relation = Column(String(100))         # renamed from 'relationship'
    phone = Column(String(20), nullable=False)
    alternate_phone = Column(String(20))
    email = Column(String(255))
    address = Column(Text)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    patient = relationship("Patient", back_populates="emergency_contacts")
