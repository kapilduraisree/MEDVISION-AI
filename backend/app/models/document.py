from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    family_member_id = Column(Integer, ForeignKey("family_members.id"), nullable=True)
    category = Column(String(100))
    title = Column(String(500), nullable=False)
    description = Column(Text)
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(500))
    file_type = Column(String(20))
    file_size_kb = Column(Integer)
    document_date = Column(DateTime)
    tags = Column(String(500))
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    patient = relationship("Patient", back_populates="documents")
    family_member = relationship("FamilyMember", back_populates="documents")
