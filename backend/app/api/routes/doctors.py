from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_doctor, get_current_user
from app.models.doctor import Doctor, DoctorNote
from app.models.patient import Patient
from app.models.report import MedicalReport, ReportValue
from app.models.user import User
from app.models.appointment import Appointment
from app.models.notification import Notification

router = APIRouter()


class DoctorProfileUpdate(BaseModel):
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    hospital_name: Optional[str] = None
    hospital_address: Optional[str] = None
    city: Optional[str] = None
    years_of_experience: Optional[int] = None
    consultation_fee: Optional[float] = None
    available_days: Optional[str] = None
    available_time_start: Optional[str] = None
    available_time_end: Optional[str] = None
    bio: Optional[str] = None


class DoctorNoteCreate(BaseModel):
    patient_id: int
    note_text: str
    follow_up_date: Optional[str] = None
    report_id: Optional[int] = None
    appointment_id: Optional[int] = None
    is_approved_summary: bool = False
    approved_summary_text: Optional[str] = None


@router.get("/profile")
def get_doctor_profile(
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "phone": current_user.phone,
        },
        "doctor": {
            "id": doctor.id,
            "specialization": doctor.specialization,
            "qualification": doctor.qualification,
            "registration_number": doctor.registration_number,
            "hospital_name": doctor.hospital_name,
            "city": doctor.city,
            "years_of_experience": doctor.years_of_experience,
            "consultation_fee": doctor.consultation_fee,
            "available_days": doctor.available_days,
            "is_verified": doctor.is_verified,
            "is_available": doctor.is_available,
        },
    }


@router.put("/profile")
def update_doctor_profile(
    data: DoctorProfileUpdate,
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        # Create doctor profile
        doctor = Doctor(user_id=current_user.id)
        db.add(doctor)
        db.flush()

    for field, value in data.dict(exclude_none=True).items():
        setattr(doctor, field, value)
    db.commit()
    return {"message": "Profile updated"}


@router.get("/dashboard")
def doctor_dashboard(
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    from datetime import datetime
    upcoming = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date >= datetime.utcnow(),
            Appointment.status.in_(["requested", "confirmed"]),
        )
        .order_by(Appointment.appointment_date)
        .limit(10)
        .all()
    )

    pending_requests = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.id,
        Appointment.status == "requested",
    ).count()

    from app.models.notification import Notification
    unread_notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).count()

    return {
        "doctor_name": current_user.full_name,
        "specialization": doctor.specialization,
        "upcoming_appointments": len(upcoming),
        "pending_requests": pending_requests,
        "unread_notifications": unread_notifications,
        "appointments": [
            {
                "id": a.id,
                "patient_id": a.patient_id,
                "appointment_date": a.appointment_date,
                "reason": a.reason,
                "status": a.status,
            }
            for a in upcoming
        ],
    }


@router.get("/patients/{patient_id}")
def view_patient(
    patient_id: int,
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    """View a patient's full medical data."""
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()

    # Check authorization (doctor must have appointment with patient)
    appointment = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.id,
        Appointment.patient_id == patient_id,
    ).first()
    if not appointment and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this patient")

    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient_user = db.query(User).filter(User.id == patient.user_id).first()

    # Get recent reports
    reports = (
        db.query(MedicalReport)
        .filter(MedicalReport.patient_id == patient_id)
        .order_by(MedicalReport.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "patient": {
            "id": patient.id,
            "name": patient_user.full_name if patient_user else "",
            "email": patient_user.email if patient_user else "",
            "blood_group": patient.blood_group,
            "known_allergies": patient.known_allergies,
            "chronic_conditions": patient.chronic_conditions,
            "current_medications": patient.current_medications,
        },
        "recent_reports": [
            {
                "id": r.id,
                "report_type": r.report_type,
                "report_date": r.report_date,
                "summary": r.summary,
                "is_doctor_reviewed": r.is_doctor_reviewed,
            }
            for r in reports
        ],
    }


@router.post("/notes")
def add_doctor_note(
    data: DoctorNoteCreate,
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()

    from datetime import datetime
    follow_up = None
    if data.follow_up_date:
        try:
            follow_up = datetime.fromisoformat(data.follow_up_date)
        except Exception:
            pass

    note = DoctorNote(
        doctor_id=doctor.id,
        patient_id=data.patient_id,
        note_text=data.note_text,
        follow_up_date=follow_up,
        report_id=data.report_id,
        appointment_id=data.appointment_id,
        is_approved_summary=data.is_approved_summary,
        approved_summary_text=data.approved_summary_text,
    )
    db.add(note)

    # Mark report as reviewed
    if data.report_id:
        report = db.query(MedicalReport).filter(MedicalReport.id == data.report_id).first()
        if report:
            report.is_doctor_reviewed = True
            report.is_approved = data.is_approved_summary

    # Notify patient
    patient = db.query(Patient).filter(Patient.id == data.patient_id).first()
    if patient:
        db.add(Notification(
            user_id=patient.user_id,
            title="Doctor Note Added",
            message=f"Dr. {current_user.full_name} has added a note to your record.",
            notification_type="doctor_note",
            reference_id=note.id if note.id else None,
            reference_type="doctor_note",
        ))

    db.commit()
    return {"message": "Note added successfully"}
