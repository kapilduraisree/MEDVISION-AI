from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List
import os, shutil, uuid
from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin
from app.core.config import settings
from app.models.medicine import Medicine
from app.models.user import User
from app.services.ai.medicine_scanner import scan_medicine_strip

router = APIRouter()


@router.get("/search")
def search_medicines(
    q: str = Query(..., min_length=2),
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    medicines = (
        db.query(Medicine)
        .filter(
            Medicine.brand_name.ilike(f"%{q}%") |
            Medicine.generic_name.ilike(f"%{q}%") |
            Medicine.active_ingredient.ilike(f"%{q}%")
        )
        .limit(limit)
        .all()
    )
    return {"results": [_format_medicine(m) for m in medicines]}


@router.get("/{medicine_id}")
def get_medicine_detail(
    medicine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")

    return {
        **_format_medicine(medicine),
        "disclaimer": (
            "ℹ️ This information is from the MedVision verified medicine database. "
            "Do not use this as a prescription. Always follow your doctor's advice."
        ),
    }


@router.post("/scan-strip")
def scan_medicine(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Scan a medicine strip/packaging image and extract information."""
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only image files allowed")

    save_dir = os.path.join(settings.UPLOAD_DIR, "medicines")
    os.makedirs(save_dir, exist_ok=True)
    ext = file.filename.split(".")[-1]
    filename = f"med_{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(save_dir, filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = scan_medicine_strip(save_path)
    result["file_path"] = f"/uploads/medicines/{filename}"
    return result


def _format_medicine(m: Medicine) -> dict:
    return {
        "id": m.id,
        "brand_name": m.brand_name,
        "generic_name": m.generic_name,
        "active_ingredient": m.active_ingredient,
        "drug_category": m.drug_category,
        "general_purpose": m.general_purpose,
        "common_precautions": m.common_precautions,
        "common_side_effects": m.common_side_effects,
        "storage_information": m.storage_information,
        "important_warnings": m.important_warnings,
        "manufacturer": m.manufacturer,
        "drug_class": m.drug_class,
        "is_otc": m.is_otc,
        "requires_prescription": m.requires_prescription,
        "is_verified": m.is_verified,
        "source": m.source,
    }
