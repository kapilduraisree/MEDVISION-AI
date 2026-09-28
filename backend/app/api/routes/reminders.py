from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from app.core.database import get_db
from app.core.security import get_current_patient
from app.models.patient import Patient
from app.models.reminder import MedicationSchedule, MedicationLog
from app.models.user import User
import json

router = APIRouter()


class ScheduleCreate(BaseModel):
    medicine_name: str
    strength: Optional[str] = None
    frequency: str
    times: List[str]  # ["08:00", "20:00"]
    start_date: date
    end_date: Optional[date] = None
    instructions: Optional[str] = None
    before_after_food: Optional[str] = None
    family_member_id: Optional[int] = None


class LogUpdate(BaseModel):
    status: str  # taken, skipped
    notes: Optional[str] = None


@router.post("/")
def create_schedule(
    data: ScheduleCreate,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    schedule = MedicationSchedule(
        patient_id=patient.id,
        family_member_id=data.family_member_id,
        medicine_name=data.medicine_name,
        strength=data.strength,
        frequency=data.frequency,
        times=json.dumps(data.times),
        start_date=data.start_date,
        end_date=data.end_date,
        instructions=data.instructions,
        before_after_food=data.before_after_food,
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return {"message": "Reminder schedule created", "schedule_id": schedule.id}


@router.get("/")
def list_schedules(
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    schedules = (
        db.query(MedicationSchedule)
        .filter(
            MedicationSchedule.patient_id == patient.id,
            MedicationSchedule.is_active == True,
        )
        .all()
    )
    return {
        "schedules": [
            {
                "id": s.id,
                "medicine_name": s.medicine_name,
                "strength": s.strength,
                "frequency": s.frequency,
                "times": json.loads(s.times) if s.times else [],
                "start_date": s.start_date,
                "end_date": s.end_date,
                "instructions": s.instructions,
                "before_after_food": s.before_after_food,
                "is_active": s.is_active,
            }
            for s in schedules
        ]
    }


@router.delete("/{schedule_id}")
def deactivate_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    schedule = db.query(MedicationSchedule).filter(
        MedicationSchedule.id == schedule_id,
        MedicationSchedule.patient_id == patient.id,
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    schedule.is_active = False
    db.commit()
    return {"message": "Schedule deactivated"}


@router.post("/{schedule_id}/log")
def log_medication(
    schedule_id: int,
    data: LogUpdate,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    schedule = db.query(MedicationSchedule).filter(
        MedicationSchedule.id == schedule_id,
        MedicationSchedule.patient_id == patient.id,
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    log = MedicationLog(
        schedule_id=schedule_id,
        scheduled_time=datetime.utcnow(),
        status=data.status,
        taken_at=datetime.utcnow() if data.status == "taken" else None,
        notes=data.notes,
    )
    db.add(log)
    db.commit()
    return {"message": f"Medication marked as {data.status}"}


@router.get("/{schedule_id}/adherence")
def get_adherence(
    schedule_id: int,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    schedule = db.query(MedicationSchedule).filter(
        MedicationSchedule.id == schedule_id,
        MedicationSchedule.patient_id == patient.id,
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    logs = db.query(MedicationLog).filter(MedicationLog.schedule_id == schedule_id).all()
    total = len(logs)
    taken = sum(1 for l in logs if l.status == "taken")
    skipped = sum(1 for l in logs if l.status == "skipped")
    missed = sum(1 for l in logs if l.status == "missed")

    adherence_pct = (taken / total * 100) if total > 0 else 0

    return {
        "schedule_id": schedule_id,
        "medicine_name": schedule.medicine_name,
        "total_doses": total,
        "taken": taken,
        "skipped": skipped,
        "missed": missed,
        "adherence_percentage": round(adherence_pct, 1),
    }
