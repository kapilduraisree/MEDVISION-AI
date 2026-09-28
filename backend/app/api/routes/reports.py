from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import os, shutil, uuid
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_patient, get_current_user
from app.core.config import settings
from app.models.patient import Patient
from app.models.report import MedicalReport, ReportValue
from app.models.user import User
from app.services.ai.ocr_service import extract_text_from_file, parse_lab_values, categorize_value
from app.services.ai.report_explainer import (
    explain_test_value, generate_report_summary, generate_doctor_questions
)

router = APIRouter()


@router.post("/upload")
def upload_report(
    file: UploadFile = File(...),
    report_type: str = Form("blood_test"),
    report_date: Optional[str] = Form(None),
    lab_name: Optional[str] = Form(""),
    family_member_id: Optional[int] = Form(None),
    language: str = Form("en"),
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    # Validate file type
    allowed_types = ["application/pdf", "image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PDF, JPG, PNG files are allowed")

    # Save file
    ext = file.filename.split(".")[-1]
    filename = f"report_{patient.id}_{uuid.uuid4().hex}.{ext}"
    save_dir = os.path.join(settings.UPLOAD_DIR, "reports")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # OCR extraction
    ocr_result = extract_text_from_file(save_path)
    raw_text = ocr_result.get("text", "")
    confidence = ocr_result.get("confidence", 0)

    # Parse lab values
    parsed_values = parse_lab_values(raw_text)

    # Create report record
    report_dt = None
    if report_date:
        try:
            report_dt = datetime.fromisoformat(report_date)
        except Exception:
            report_dt = datetime.utcnow()

    report = MedicalReport(
        patient_id=patient.id,
        family_member_id=family_member_id,
        report_type=report_type,
        report_date=report_dt or datetime.utcnow(),
        lab_name=lab_name,
        file_path=f"/uploads/reports/{filename}",
        file_type=ext,
        original_filename=file.filename,
        ocr_raw_text=raw_text,
        ocr_confidence=confidence,
    )
    db.add(report)
    db.flush()

    # Create report values
    report_value_objects = []
    for v in parsed_values:
        status = categorize_value(v.get("result", ""), v.get("reference_range_text", ""))
        explanation_en = explain_test_value(
            v.get("test_name", ""), v.get("result", ""),
            v.get("unit", ""), v.get("reference_range_text", ""),
            status, "en"
        )
        explanation_ta = explain_test_value(
            v.get("test_name", ""), v.get("result", ""),
            v.get("unit", ""), v.get("reference_range_text", ""),
            status, "ta"
        )

        rv = ReportValue(
            report_id=report.id,
            test_name=v.get("test_name", ""),
            result=v.get("result", ""),
            unit=v.get("unit", ""),
            reference_range_text=v.get("reference_range_text", ""),
            status=status,
            explanation=explanation_en,
            explanation_tamil=explanation_ta,
        )
        db.add(rv)
        report_value_objects.append({
            "test_name": v.get("test_name"), "result": v.get("result"),
            "unit": v.get("unit"), "status": status,
        })

    # Generate summary
    summary = generate_report_summary(report_value_objects, language)
    questions = generate_doctor_questions(report_value_objects, language)

    report.summary = summary
    import json
    report.ai_questions_for_doctor = json.dumps(questions)

    db.commit()
    db.refresh(report)

    return {
        "report_id": report.id,
        "ocr_confidence": confidence,
        "low_confidence": confidence < 0.7,
        "values_extracted": len(parsed_values),
        "summary": summary,
        "questions_for_doctor": questions,
        "file_path": report.file_path,
        "disclaimer": (
            "⚠️ This extraction is for informational purposes only. "
            "Please verify with your doctor."
        ),
    }


@router.get("/")
def list_reports(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    reports = (
        db.query(MedicalReport)
        .filter(MedicalReport.patient_id == patient.id)
        .order_by(MedicalReport.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    total = db.query(MedicalReport).filter(MedicalReport.patient_id == patient.id).count()

    return {
        "total": total,
        "reports": [
            {
                "id": r.id,
                "report_type": r.report_type,
                "lab_name": r.lab_name,
                "report_date": r.report_date,
                "ocr_confidence": r.ocr_confidence,
                "file_path": r.file_path,
                "is_doctor_reviewed": r.is_doctor_reviewed,
                "created_at": r.created_at,
            }
            for r in reports
        ],
    }


@router.get("/{report_id}")
def get_report_detail(
    report_id: int,
    language: str = "en",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Access control
    if current_user.role == "patient":
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient or report.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="Access denied")

    values = db.query(ReportValue).filter(ReportValue.report_id == report_id).all()
    import json

    questions = []
    if report.ai_questions_for_doctor:
        try:
            questions = json.loads(report.ai_questions_for_doctor)
        except Exception:
            questions = []

    return {
        "report": {
            "id": report.id,
            "report_type": report.report_type,
            "lab_name": report.lab_name,
            "report_date": report.report_date,
            "file_path": report.file_path,
            "ocr_confidence": report.ocr_confidence,
            "is_ocr_verified": report.is_ocr_verified,
            "summary": report.summary,
            "ai_explanation": report.ai_explanation_tamil if language == "ta" else report.ai_explanation,
            "questions_for_doctor": questions,
            "is_doctor_reviewed": report.is_doctor_reviewed,
            "created_at": report.created_at,
        },
        "values": [
            {
                "id": v.id,
                "test_name": v.test_name,
                "result": v.result,
                "unit": v.unit,
                "reference_range_text": v.reference_range_text,
                "status": v.status,
                "explanation": v.explanation_tamil if language == "ta" else v.explanation,
                "is_manually_corrected": v.is_manually_corrected,
            }
            for v in values
        ],
        "disclaimer": (
            "⚠️ This is AI-generated information for educational purposes only. "
            "Please consult your doctor for medical advice."
        ),
    }


@router.put("/{report_id}/values/{value_id}")
def correct_report_value(
    report_id: int,
    value_id: int,
    result: str,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    """Allow user to manually correct OCR mistakes."""
    rv = db.query(ReportValue).filter(
        ReportValue.id == value_id,
        ReportValue.report_id == report_id
    ).first()
    if not rv:
        raise HTTPException(status_code=404, detail="Value not found")

    rv.result = result
    rv.is_manually_corrected = True
    # Re-categorize
    rv.status = categorize_value(result, rv.reference_range_text or "")
    db.commit()

    return {"message": "Value corrected", "new_status": rv.status}
