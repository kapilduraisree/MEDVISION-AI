from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class HealthMetric(Base):
    __tablename__ = "health_metrics"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    family_member_id = Column(Integer, ForeignKey("family_members.id"), nullable=True)
    metric_name = Column(String(200), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50))
    recorded_date = Column(DateTime, nullable=False)
    source = Column(String(100), default="manual")
    report_id = Column(Integer, ForeignKey("medical_reports.id"), nullable=True)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    patient = relationship("Patient", back_populates="health_metrics")
