from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user, get_current_patient, get_current_doctor
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.user import User
from app.models.notification import Notification

router = APIRouter()


class AppointmentCreate(BaseModel):
    doctor_id: int
    appointment_date: datetime
    reason: Optional[str] = None
    family_member_id: Optional[int] = None


class AppointmentUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None


@router.post("/")
def create_appointment(
    data: AppointmentCreate,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    doctor = db.query(Doctor).filter(Doctor.id == data.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    appointment = Appointment(
        patient_id=patient.id,
        family_member_id=data.family_member_id,
        doctor_id=data.doctor_id,
        appointment_date=data.appointment_date,
        reason=data.reason,
        status="requested",
    )
    db.add(appointment)
    db.flush()

    # Notify doctor
    db.add(Notification(
        user_id=doctor.user_id,
        title="New Appointment Request",
        message=f"New appointment request from {current_user.full_name} on {data.appointment_date.strftime('%Y-%m-%d %H:%M')}",
        notification_type="appointment",
        reference_id=appointment.id,
        reference_type="appointment",
    ))
    db.commit()

    return {"message": "Appointment requested", "appointment_id": appointment.id}


@router.get("/")
def list_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == "patient":
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        appointments = (
            db.query(Appointment)
            .filter(Appointment.patient_id == patient.id)
            .order_by(Appointment.appointment_date.desc())
            .all()
        )
    elif current_user.role == "doctor":
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        appointments = (
            db.query(Appointment)
            .filter(Appointment.doctor_id == doctor.id)
            .order_by(Appointment.appointment_date.desc())
            .all()
        )
    else:
        appointments = db.query(Appointment).order_by(Appointment.appointment_date.desc()).all()

    return {
        "appointments": [
            {
                "id": a.id,
                "patient_id": a.patient_id,
                "doctor_id": a.doctor_id,
                "appointment_date": a.appointment_date,
                "reason": a.reason,
                "status": a.status,
                "notes": a.notes,
                "follow_up_date": a.follow_up_date,
                "created_at": a.created_at,
            }
            for a in appointments
        ]
    }


@router.put("/{appointment_id}")
def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if data.status:
        appointment.status = data.status
    if data.notes:
        appointment.notes = data.notes
    if data.follow_up_date:
        appointment.follow_up_date = data.follow_up_date

    # Notify patient on status change
    if data.status and current_user.role == "doctor":
        patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
        db.add(Notification(
            user_id=patient.user_id,
            title="Appointment Update",
            message=f"Your appointment status has been updated to: {data.status}",
            notification_type="appointment",
            reference_id=appointment.id,
            reference_type="appointment",
        ))

    db.commit()
    return {"message": "Appointment updated"}


@router.get("/doctors/search")
def search_doctors(
    specialization: Optional[str] = None,
    city: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Doctor, User).join(User, Doctor.user_id == User.id).filter(
        Doctor.is_available == True,
        User.is_active == True,
    )
    if specialization:
        query = query.filter(Doctor.specialization.ilike(f"%{specialization}%"))
    if city:
        query = query.filter(Doctor.city.ilike(f"%{city}%"))

    results = query.limit(20).all()
    return {
        "doctors": [
            {
                "id": d.id,
                "name": u.full_name,
                "specialization": d.specialization,
                "hospital_name": d.hospital_name,
                "city": d.city,
                "years_of_experience": d.years_of_experience,
                "consultation_fee": d.consultation_fee,
                "available_days": d.available_days,
            }
            for d, u in results
        ]
    }
