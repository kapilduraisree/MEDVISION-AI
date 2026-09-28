from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.sql import func
from app.core.database import Base


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    brand_name = Column(String(300), nullable=False, index=True)
    generic_name = Column(String(300), index=True)
    active_ingredient = Column(String(300))
    drug_category = Column(String(200))
    general_purpose = Column(Text)
    common_precautions = Column(Text)
    common_side_effects = Column(Text)
    storage_information = Column(Text)
    important_warnings = Column(Text)
    manufacturer = Column(String(300))
    drug_class = Column(String(200))
    is_otc = Column(Boolean, default=False)
    is_controlled = Column(Boolean, default=False)
    requires_prescription = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=True)
    source = Column(String(200), default="MedVision Medicine Database")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class DrugInteraction(Base):
    __tablename__ = "drug_interactions"

    id = Column(Integer, primary_key=True, index=True)
    drug_a = Column(String(300), nullable=False)
    drug_b = Column(String(300), nullable=False)
    interaction_severity = Column(String(50))
    mechanism = Column(Text)
    effect = Column(Text)
    clinical_significance = Column(Text)
    recommended_action = Column(Text)
    source = Column(String(300))
    created_at = Column(DateTime, server_default=func.now())
