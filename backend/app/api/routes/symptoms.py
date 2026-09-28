from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_patient
from app.models.patient import Patient
from app.models.symptom import Symptom
from app.models.user import User
from app.models.notification import Notification

router = APIRouter()

# Emergency keywords that should trigger urgent care message
EMERGENCY_SYMPTOMS = [
    "chest pain", "heart attack", "cannot breathe", "can't breathe",
    "severe bleeding", "unconscious", "stroke", "seizure", "overdose",
    "anaphylaxis", "severe chest", "difficulty breathing",
    "நெஞ்சு வலி", "மூச்சு", "மயக்கம்",
]


class SymptomCreate(BaseModel):
    description: str
    input_method: str = "text"
    voice_transcript: Optional[str] = None
    duration: Optional[str] = None
    severity: Optional[str] = None  # mild, moderate, severe
    location_on_body: Optional[str] = None
    language: str = "en"
    family_member_id: Optional[int] = None


@router.post("/")
def add_symptom(
    data: SymptomCreate,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()

    # Check for emergency keywords
    is_emergency = any(kw in data.description.lower() for kw in EMERGENCY_SYMPTOMS)

    symptom = Symptom(
        patient_id=patient.id,
        family_member_id=data.family_member_id,
        description=data.description,
        input_method=data.input_method,
        voice_transcript=data.voice_transcript,
        duration=data.duration,
        severity=data.severity,
        location_on_body=data.location_on_body,
        language=data.language,
        is_emergency_flagged=is_emergency,
        emergency_reason="Emergency keywords detected in symptom description" if is_emergency else None,
    )
    db.add(symptom)
    db.flush()

    emergency_message = None
    if is_emergency:
        emergency_message = (
            "🚨 This may require urgent medical attention. "
            "Please contact local emergency services (112) or seek immediate medical care. "
            "This system cannot provide emergency diagnosis."
        )
        db.add(Notification(
            user_id=current_user.id,
            title="Emergency Alert",
            message=emergency_message,
            notification_type="emergency",
            reference_id=symptom.id,
            reference_type="symptom",
        ))

    db.commit()
    db.refresh(symptom)

    return {
        "symptom_id": symptom.id,
        "is_emergency_flagged": is_emergency,
        "emergency_message": emergency_message,
        "disclaimer": (
            "⚠️ This system does not diagnose medical conditions. "
            "Please consult a qualified healthcare professional."
        ),
    }


@router.get("/")
def list_symptoms(
    limit: int = 20,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    symptoms = (
        db.query(Symptom)
        .filter(Symptom.patient_id == patient.id)
        .order_by(Symptom.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "symptoms": [
            {
                "id": s.id,
                "description": s.description,
                "input_method": s.input_method,
                "duration": s.duration,
                "severity": s.severity,
                "is_emergency_flagged": s.is_emergency_flagged,
                "created_at": s.created_at,
            }
            for s in symptoms
        ]
    }
