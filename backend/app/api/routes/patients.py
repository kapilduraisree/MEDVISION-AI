from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.core.database import get_db
from app.core.security import get_current_user, get_current_patient
from app.models.patient import Patient
from app.models.user import User

router = APIRouter()


class PatientProfileUpdate(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    occupation: Optional[str] = None
    marital_status: Optional[str] = None
    known_allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    current_medications: Optional[str] = None
    family_medical_history: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_id: Optional[str] = None


@router.get("/profile")
def get_patient_profile(
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "phone": current_user.phone,
            "profile_image": current_user.profile_image,
            "preferred_language": current_user.preferred_language,
        },
        "patient": {
            "id": patient.id,
            "date_of_birth": patient.date_of_birth,
            "gender": patient.gender,
            "blood_group": patient.blood_group,
            "height_cm": patient.height_cm,
            "weight_kg": patient.weight_kg,
            "address": patient.address,
            "city": patient.city,
            "state": patient.state,
            "country": patient.country,
            "pincode": patient.pincode,
            "occupation": patient.occupation,
            "marital_status": patient.marital_status,
            "known_allergies": patient.known_allergies,
            "chronic_conditions": patient.chronic_conditions,
            "current_medications": patient.current_medications,
            "family_medical_history": patient.family_medical_history,
            "insurance_provider": patient.insurance_provider,
            "insurance_id": patient.insurance_id,
        },
    }


@router.put("/profile")
def update_patient_profile(
    data: PatientProfileUpdate,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    update_data = data.dict(exclude_none=True)
    for field, value in update_data.items():
        setattr(patient, field, value)

    db.commit()
    return {"message": "Profile updated successfully"}


@router.get("/dashboard-summary")
def get_dashboard_summary(
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    """Get summary data for patient dashboard."""
    from app.models.report import MedicalReport, ReportValue
    from app.models.reminder import MedicationSchedule
    from app.models.appointment import Appointment
    from app.models.symptom import Symptom
    from app.models.notification import Notification
    from datetime import datetime

    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    # Recent reports
    recent_reports = (
        db.query(MedicalReport)
        .filter(MedicalReport.patient_id == patient.id)
        .order_by(MedicalReport.created_at.desc())
        .limit(5)
        .all()
    )

    # Abnormal values from latest report
    abnormal_values = []
    if recent_reports:
        latest_report = recent_reports[0]
        abnormal_values = (
            db.query(ReportValue)
            .filter(
                ReportValue.report_id == latest_report.id,
                ReportValue.status.in_(["attention", "abnormal"]),
            )
            .all()
        )

    # Active medication schedules
    active_meds = (
        db.query(MedicationSchedule)
        .filter(
            MedicationSchedule.patient_id == patient.id,
            MedicationSchedule.is_active == True,
        )
        .all()
    )

    # Upcoming appointments
    upcoming_appointments = (
        db.query(Appointment)
        .filter(
            Appointment.patient_id == patient.id,
            Appointment.appointment_date >= datetime.utcnow(),
            Appointment.status.in_(["requested", "confirmed"]),
        )
        .order_by(Appointment.appointment_date)
        .limit(3)
        .all()
    )

    # Unread notifications
    unread_notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
        .count()
    )

    return {
        "patient_id": patient.id,
        "full_name": current_user.full_name,
        "blood_group": patient.blood_group,
        "total_reports": len(recent_reports),
        "abnormal_count": len(abnormal_values),
        "active_medications": len(active_meds),
        "upcoming_appointments": len(upcoming_appointments),
        "unread_notifications": unread_notifications,
        "recent_reports": [
            {
                "id": r.id,
                "report_type": r.report_type,
                "report_date": r.report_date,
                "created_at": r.created_at,
            }
            for r in recent_reports
        ],
        "abnormal_values": [
            {
                "test_name": v.test_name,
                "result": v.result,
                "unit": v.unit,
                "status": v.status,
            }
            for v in abnormal_values
        ],
        "active_medications": [
            {
                "medicine_name": m.medicine_name,
                "frequency": m.frequency,
                "times": m.times,
            }
            for m in active_meds[:5]
        ],
    }
