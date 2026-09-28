from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import os, shutil, uuid
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_patient
from app.core.config import settings
from app.models.patient import Patient
from app.models.prescription import Prescription, PrescriptionItem
from app.models.user import User
from app.services.ai.prescription_analyzer import analyze_prescription

router = APIRouter()


@router.post("/upload")
def upload_prescription(
    file: UploadFile = File(...),
    family_member_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PDF, JPG, PNG files are allowed")

    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()

    ext = file.filename.split(".")[-1]
    filename = f"rx_{patient.id}_{uuid.uuid4().hex}.{ext}"
    save_dir = os.path.join(settings.UPLOAD_DIR, "prescriptions")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Analyze prescription
    analysis = analyze_prescription(save_path)

    prescription = Prescription(
        patient_id=patient.id,
        family_member_id=family_member_id,
        file_path=f"/uploads/prescriptions/{filename}",
        original_filename=file.filename,
        ocr_raw_text=analysis["raw_text"],
        ocr_confidence=analysis["confidence"],
        prescription_date=datetime.utcnow(),
    )
    db.add(prescription)
    db.flush()

    # Add prescription items
    for item in analysis["items"]:
        pi = PrescriptionItem(
            prescription_id=prescription.id,
            medicine_name=item.get("medicine_name", ""),
            strength=item.get("strength", ""),
            dosage_instruction=item.get("dosage_instruction", ""),
            frequency=item.get("frequency", ""),
            duration=item.get("duration", ""),
            before_after_food=item.get("before_after_food", ""),
            doctor_notes=item.get("doctor_notes", ""),
            ocr_confidence=item.get("ocr_confidence", 0),
            needs_verification=item.get("needs_verification", True),
        )
        db.add(pi)

    db.commit()
    db.refresh(prescription)

    return {
        "prescription_id": prescription.id,
        "items": analysis["items"],
        "confidence": analysis["confidence"],
        "low_confidence": analysis["low_confidence"],
        "disclaimer": analysis["disclaimer"],
        "file_path": prescription.file_path,
    }


@router.get("/")
def list_prescriptions(
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    prescriptions = (
        db.query(Prescription)
        .filter(Prescription.patient_id == patient.id)
        .order_by(Prescription.created_at.desc())
        .all()
    )
    return {
        "prescriptions": [
            {
                "id": p.id,
                "prescription_date": p.prescription_date,
                "file_path": p.file_path,
                "ocr_confidence": p.ocr_confidence,
                "is_user_verified": p.is_user_verified,
                "created_at": p.created_at,
                "item_count": len(p.items),
            }
            for p in prescriptions
        ]
    }


@router.get("/{prescription_id}")
def get_prescription(
    prescription_id: int,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    prescription = db.query(Prescription).filter(
        Prescription.id == prescription_id,
        Prescription.patient_id == patient.id,
    ).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    return {
        "prescription": {
            "id": prescription.id,
            "prescription_date": prescription.prescription_date,
            "file_path": prescription.file_path,
            "ocr_confidence": prescription.ocr_confidence,
            "is_user_verified": prescription.is_user_verified,
        },
        "items": [
            {
                "id": i.id,
                "medicine_name": i.medicine_name,
                "strength": i.strength,
                "dosage_instruction": i.dosage_instruction,
                "frequency": i.frequency,
                "duration": i.duration,
                "before_after_food": i.before_after_food,
                "doctor_notes": i.doctor_notes,
                "needs_verification": i.needs_verification,
                "is_user_confirmed": i.is_user_confirmed,
            }
            for i in prescription.items
        ],
        "disclaimer": (
            "⚠️ Please verify all extracted prescription information with your "
            "doctor or pharmacist before taking any medication."
        ),
    }


@router.put("/{prescription_id}/verify")
def mark_as_verified(
    prescription_id: int,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    prescription = db.query(Prescription).filter(
        Prescription.id == prescription_id,
        Prescription.patient_id == patient.id,
    ).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    prescription.is_user_verified = True
    for item in prescription.items:
        item.is_user_confirmed = True
    db.commit()
    return {"message": "Prescription marked as verified"}
