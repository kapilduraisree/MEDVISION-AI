from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.core.database import get_db
from app.core.security import get_current_patient
from app.models.patient import Patient, FamilyMember
from app.models.user import User

router = APIRouter()


class FamilyMemberCreate(BaseModel):
    name: str
    relationship: str = ""
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    known_allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    current_medications: Optional[str] = None


@router.post("/")
def add_family_member(
    data: FamilyMemberCreate,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    member = FamilyMember(
        patient_id=patient.id,
        name=data.name,
        relation=data.relationship,
        date_of_birth=data.date_of_birth,
        gender=data.gender,
        blood_group=data.blood_group,
        known_allergies=data.known_allergies,
        chronic_conditions=data.chronic_conditions,
        current_medications=data.current_medications,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return {"message": "Family member added", "member_id": member.id}


@router.get("/")
def list_family_members(
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    members = db.query(FamilyMember).filter(
        FamilyMember.patient_id == patient.id,
        FamilyMember.is_active == True,
    ).all()
    return {
        "members": [
            {
                "id": m.id,
                "name": m.name,
                "relationship": m.relation,
                "date_of_birth": m.date_of_birth,
                "gender": m.gender,
                "blood_group": m.blood_group,
                "known_allergies": m.known_allergies,
                "chronic_conditions": m.chronic_conditions,
            }
            for m in members
        ]
    }


@router.put("/{member_id}")
def update_family_member(
    member_id: int,
    data: FamilyMemberCreate,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    member = db.query(FamilyMember).filter(
        FamilyMember.id == member_id,
        FamilyMember.patient_id == patient.id,
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Family member not found")

    member.name = data.name
    member.relation = data.relationship
    if data.date_of_birth is not None: member.date_of_birth = data.date_of_birth
    if data.gender is not None: member.gender = data.gender
    if data.blood_group is not None: member.blood_group = data.blood_group
    if data.known_allergies is not None: member.known_allergies = data.known_allergies
    if data.chronic_conditions is not None: member.chronic_conditions = data.chronic_conditions
    if data.current_medications is not None: member.current_medications = data.current_medications
    db.commit()
    return {"message": "Family member updated"}


@router.delete("/{member_id}")
def remove_family_member(
    member_id: int,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    member = db.query(FamilyMember).filter(
        FamilyMember.id == member_id,
        FamilyMember.patient_id == patient.id,
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Family member not found")
    member.is_active = False
    db.commit()
    return {"message": "Family member removed"}
