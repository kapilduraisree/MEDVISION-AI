from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_patient
from app.models.patient import Patient
from app.models.emergency import EmergencyContact
from app.models.user import User

router = APIRouter()


class EmergencyContactCreate(BaseModel):
    name: str
    relationship: str = ""
    phone: str
    alternate_phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    is_primary: bool = False


@router.post("/contacts")
def add_contact(
    data: EmergencyContactCreate,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()

    if data.is_primary:
        db.query(EmergencyContact).filter(
            EmergencyContact.patient_id == patient.id,
            EmergencyContact.is_primary == True,
        ).update({"is_primary": False})

    contact = EmergencyContact(
        patient_id=patient.id,
        name=data.name,
        relation=data.relationship,
        phone=data.phone,
        alternate_phone=data.alternate_phone,
        email=data.email,
        address=data.address,
        is_primary=data.is_primary,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return {"message": "Emergency contact added", "contact_id": contact.id}


@router.get("/contacts")
def list_contacts(
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    contacts = db.query(EmergencyContact).filter(
        EmergencyContact.patient_id == patient.id
    ).all()
    return {
        "contacts": [
            {
                "id": c.id,
                "name": c.name,
                "relationship": c.relation,
                "phone": c.phone,
                "alternate_phone": c.alternate_phone,
                "email": c.email,
                "is_primary": c.is_primary,
            }
            for c in contacts
        ],
        "emergency_numbers": {
            "india_emergency": "112",
            "ambulance": "108",
            "police": "100",
            "fire": "101",
        },
        "disclaimer": (
            "⚠️ In case of a medical emergency, call 112 (India) immediately. "
            "This system cannot provide emergency medical assistance."
        ),
    }


@router.delete("/contacts/{contact_id}")
def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    contact = db.query(EmergencyContact).filter(
        EmergencyContact.id == contact_id,
        EmergencyContact.patient_id == patient.id,
    ).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted"}
