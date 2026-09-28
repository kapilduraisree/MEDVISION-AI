from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import os, shutil, uuid
from app.core.database import get_db
from app.core.security import get_current_patient
from app.core.config import settings
from app.models.patient import Patient
from app.models.document import Document
from app.models.user import User

router = APIRouter()


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("other"),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    document_date: Optional[str] = Form(None),
    family_member_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()

    allowed_types = [
        "application/pdf", "image/jpeg", "image/png", "image/jpg",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    ext = file.filename.split(".")[-1].lower()
    filename = f"doc_{patient.id}_{uuid.uuid4().hex}.{ext}"
    save_dir = os.path.join(settings.UPLOAD_DIR, "documents", category)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(save_path) // 1024  # KB

    doc_date = None
    if document_date:
        try:
            doc_date = datetime.fromisoformat(document_date)
        except Exception:
            doc_date = datetime.utcnow()

    document = Document(
        patient_id=patient.id,
        family_member_id=family_member_id,
        category=category,
        title=title,
        description=description,
        file_path=f"/uploads/documents/{category}/{filename}",
        original_filename=file.filename,
        file_type=ext,
        file_size_kb=file_size,
        document_date=doc_date or datetime.utcnow(),
        tags=tags,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "document_id": document.id,
        "file_path": document.file_path,
        "message": "Document uploaded successfully",
    }


@router.get("/")
def list_documents(
    category: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    query = db.query(Document).filter(
        Document.patient_id == patient.id,
        Document.is_deleted == False,
    )
    if category:
        query = query.filter(Document.category == category)
    if search:
        query = query.filter(
            Document.title.ilike(f"%{search}%") |
            Document.description.ilike(f"%{search}%") |
            Document.tags.ilike(f"%{search}%")
        )

    total = query.count()
    docs = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "documents": [
            {
                "id": d.id,
                "title": d.title,
                "category": d.category,
                "description": d.description,
                "file_path": d.file_path,
                "file_type": d.file_type,
                "file_size_kb": d.file_size_kb,
                "document_date": d.document_date,
                "tags": d.tags,
                "created_at": d.created_at,
            }
            for d in docs
        ],
    }


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.patient_id == patient.id,
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document.is_deleted = True
    db.commit()
    return {"message": "Document deleted"}
