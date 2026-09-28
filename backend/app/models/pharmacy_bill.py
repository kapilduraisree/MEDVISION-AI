from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PharmacyBill(Base):
    __tablename__ = "pharmacy_bills"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    file_path = Column(String(500))
    original_filename = Column(String(500))
    pharmacy_name = Column(String(300))
    bill_date = Column(DateTime)
    total_amount = Column(Float, default=0)
    ocr_raw_text = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    patient = relationship("Patient", back_populates="pharmacy_bills")
    items = relationship("PharmacyBillItem", back_populates="bill", cascade="all, delete-orphan")


class PharmacyBillItem(Base):
    __tablename__ = "pharmacy_bill_items"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("pharmacy_bills.id"), nullable=False)
    medicine_name = Column(String(300))
    quantity = Column(String(50))
    unit_price = Column(Float)
    total_price = Column(Float)
    created_at = Column(DateTime, server_default=func.now())

    bill = relationship("PharmacyBill", back_populates="items")
