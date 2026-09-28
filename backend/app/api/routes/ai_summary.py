from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_patient
from app.models.patient import Patient
from app.models.report import MedicalReport, ReportValue
from app.models.reminder import MedicationSchedule
from app.models.symptom import Symptom
from app.models.user import User
from app.services.ai.health_summary import generate_health_summary

router = APIRouter()


class SummaryRequest(BaseModel):
    language: str = "en"
    report_id: Optional[int] = None
    include_history: bool = True


@router.post("/generate")
def generate_summary(
    data: SummaryRequest,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    # Get recent symptoms
    symptoms = (
        db.query(Symptom)
        .filter(Symptom.patient_id == patient.id)
        .order_by(Symptom.created_at.desc())
        .limit(5)
        .all()
    )
    symptom_list = [
        {"description": s.description, "severity": s.severity, "duration": s.duration}
        for s in symptoms
    ]

    # Get latest report values
    report_values = []
    if data.report_id:
        report = db.query(MedicalReport).filter(
            MedicalReport.id == data.report_id,
            MedicalReport.patient_id == patient.id,
        ).first()
        if report:
            values = db.query(ReportValue).filter(ReportValue.report_id == report.id).all()
            report_values = [
                {
                    "test_name": v.test_name,
                    "result": v.result,
                    "unit": v.unit,
                    "status": v.status,
                }
                for v in values
            ]
    else:
        # Get latest report
        latest_report = (
            db.query(MedicalReport)
            .filter(MedicalReport.patient_id == patient.id)
            .order_by(MedicalReport.created_at.desc())
            .first()
        )
        if latest_report:
            values = db.query(ReportValue).filter(ReportValue.report_id == latest_report.id).all()
            report_values = [
                {
                    "test_name": v.test_name,
                    "result": v.result,
                    "unit": v.unit,
                    "status": v.status,
                }
                for v in values
            ]

    # Get current medications
    medications = (
        db.query(MedicationSchedule)
        .filter(
            MedicationSchedule.patient_id == patient.id,
            MedicationSchedule.is_active == True,
        )
        .all()
    )
    med_list = [
        {
            "medicine_name": m.medicine_name,
            "strength": m.strength,
            "frequency": m.frequency,
            "duration": str(m.end_date) if m.end_date else "Ongoing",
        }
        for m in medications
    ]

    # Get previous reports count
    previous_reports = (
        db.query(MedicalReport)
        .filter(MedicalReport.patient_id == patient.id)
        .all()
    )

    # Generate summary
    summary = generate_health_summary(
        patient_name=current_user.full_name,
        symptoms=symptom_list,
        report_values=report_values,
        medications=med_list,
        previous_reports=previous_reports,
        language=data.language,
    )

    return summary
