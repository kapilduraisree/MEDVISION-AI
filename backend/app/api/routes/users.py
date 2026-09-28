from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import os, shutil, uuid
from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash, verify_password
from app.core.config import settings
from app.models.user import User

router = APIRouter()


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    preferred_language: Optional[str] = None
    dark_mode: Optional[bool] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.put("/profile")
def update_profile(
    data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.full_name:
        current_user.full_name = data.full_name
    if data.phone:
        current_user.phone = data.phone
    if data.preferred_language:
        current_user.preferred_language = data.preferred_language
    if data.dark_mode is not None:
        current_user.dark_mode = data.dark_mode

    db.commit()
    db.refresh(current_user)
    return {"message": "Profile updated successfully"}


@router.post("/profile-image")
def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only JPEG/PNG images allowed")

    ext = file.filename.split(".")[-1]
    filename = f"profile_{current_user.id}_{uuid.uuid4().hex}.{ext}"
    save_dir = os.path.join(settings.UPLOAD_DIR, "profiles")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    current_user.profile_image = f"/uploads/profiles/{filename}"
    db.commit()

    return {"profile_image": current_user.profile_image}


@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")

    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}
