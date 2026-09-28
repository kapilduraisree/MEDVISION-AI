from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.user import User
from app.models.doctor import Doctor
from app.models.medicine import Medicine, DrugInteraction
from app.models.audit import AuditLog
from app.models.report import MedicalReport
from app.models.appointment import Appointment

router = APIRouter()


class MedicineCreate(BaseModel):
    brand_name: str
    generic_name: Optional[str] = None
    active_ingredient: Optional[str] = None
    drug_category: Optional[str] = None
    general_purpose: Optional[str] = None
    common_precautions: Optional[str] = None
    common_side_effects: Optional[str] = None
    storage_information: Optional[str] = None
    important_warnings: Optional[str] = None
    manufacturer: Optional[str] = None
    drug_class: Optional[str] = None
    is_otc: bool = False
    requires_prescription: bool = True


class DrugInteractionCreate(BaseModel):
    drug_a: str
    drug_b: str
    interaction_severity: str
    mechanism: Optional[str] = None
    effect: Optional[str] = None
    clinical_significance: Optional[str] = None
    recommended_action: Optional[str] = None
    source: Optional[str] = None


@router.get("/analytics")
def system_analytics(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    total_users       = db.query(User).count()
    total_patients    = db.query(User).filter(User.role == "patient").count()
    total_doctors     = db.query(User).filter(User.role == "doctor").count()
    total_reports     = db.query(MedicalReport).count()
    total_appointments = db.query(Appointment).count()

    # Simple last-6 users for registration chart (SQLite-safe)
    recent_users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .limit(20)
        .all()
    )

    return {
        "totals": {
            "users":        total_users,
            "patients":     total_patients,
            "doctors":      total_doctors,
            "reports":      total_reports,
            "appointments": total_appointments,
        },
        "monthly_registrations": [
            {"month": str(u.created_at)[:7], "count": 1}
            for u in recent_users
        ],
    }


@router.get("/users")
def list_users(
    role: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if search:
        query = query.filter(
            User.full_name.ilike(f"%{search}%") |
            User.email.ilike(f"%{search}%")
        )
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at,
                "last_login": u.last_login,
            }
            for u in users
        ],
    }


@router.put("/users/{user_id}/toggle-active")
def toggle_user_active(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
    user.is_active = not user.is_active
    db.add(AuditLog(
        user_id=current_user.id, action="admin_toggle_user",
        entity_type="user", entity_id=user_id,
        details=f"Set is_active={user.is_active}",
    ))
    db.commit()
    return {"message": f"User {'activated' if user.is_active else 'deactivated'}"}


@router.get("/doctors")
def list_doctors(
    verified_only: bool = False,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(Doctor, User).join(User, Doctor.user_id == User.id)
    if verified_only:
        query = query.filter(Doctor.is_verified == True)
    results = query.all()
    return {
        "doctors": [
            {
                "id": d.id,
                "name": u.full_name,
                "email": u.email,
                "specialization": d.specialization,
                "registration_number": d.registration_number,
                "is_verified": d.is_verified,
                "is_available": d.is_available,
            }
            for d, u in results
        ]
    }


@router.put("/doctors/{doctor_id}/verify")
def verify_doctor(
    doctor_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctor.is_verified = True
    db.commit()
    return {"message": "Doctor verified"}


@router.post("/medicines")
def add_medicine(
    data: MedicineCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    medicine = Medicine(**data.dict())
    db.add(medicine)
    db.commit()
    db.refresh(medicine)
    return {"message": "Medicine added", "medicine_id": medicine.id}


@router.post("/drug-interactions")
def add_drug_interaction(
    data: DrugInteractionCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    interaction = DrugInteraction(**data.dict())
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return {"message": "Drug interaction added", "id": interaction.id}


@router.get("/audit-logs")
def get_audit_logs(
    skip: int = 0,
    limit: int = 50,
    action: Optional[str] = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "logs": [
            {
                "id": l.id,
                "user_id": l.user_id,
                "action": l.action,
                "entity_type": l.entity_type,
                "entity_id": l.entity_id,
                "status": l.status,
                "created_at": l.created_at,
            }
            for l in logs
        ],
    }
