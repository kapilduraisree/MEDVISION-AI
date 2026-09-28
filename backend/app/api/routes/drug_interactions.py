from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.medicine import DrugInteraction
from app.models.user import User

router = APIRouter()


class InteractionCheckRequest(BaseModel):
    medicines: List[str]  # List of medicine names


@router.post("/check")
def check_drug_interactions(
    data: InteractionCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if len(data.medicines) < 2:
        raise HTTPException(status_code=400, detail="Please provide at least 2 medicines to check")

    interactions_found = []
    duplicate_warnings = []

    # Check all pairs
    for i in range(len(data.medicines)):
        for j in range(i + 1, len(data.medicines)):
            drug_a = data.medicines[i].lower().strip()
            drug_b = data.medicines[j].lower().strip()

            interaction = (
                db.query(DrugInteraction)
                .filter(
                    (DrugInteraction.drug_a.ilike(f"%{drug_a}%") &
                     DrugInteraction.drug_b.ilike(f"%{drug_b}%")) |
                    (DrugInteraction.drug_a.ilike(f"%{drug_b}%") &
                     DrugInteraction.drug_b.ilike(f"%{drug_a}%"))
                )
                .first()
            )

            if interaction:
                interactions_found.append({
                    "drug_a": data.medicines[i],
                    "drug_b": data.medicines[j],
                    "severity": interaction.interaction_severity,
                    "effect": interaction.effect,
                    "mechanism": interaction.mechanism,
                    "recommended_action": interaction.recommended_action,
                    "clinical_significance": interaction.clinical_significance,
                    "source": interaction.source,
                })

    # Check for duplicate active ingredients
    from app.models.medicine import Medicine
    ingredient_map = {}
    for med_name in data.medicines:
        medicine = (
            db.query(Medicine)
            .filter(Medicine.brand_name.ilike(f"%{med_name}%"))
            .first()
        )
        if medicine and medicine.active_ingredient:
            ingredient = medicine.active_ingredient.lower().strip()
            if ingredient in ingredient_map:
                duplicate_warnings.append({
                    "medicine_a": ingredient_map[ingredient],
                    "medicine_b": med_name,
                    "active_ingredient": medicine.active_ingredient,
                    "warning": (
                        "⚠️ Possible duplicate active ingredient detected. "
                        "Please verify with your doctor or pharmacist."
                    ),
                })
            else:
                ingredient_map[ingredient] = med_name

    return {
        "medicines_checked": data.medicines,
        "interactions_found": interactions_found,
        "duplicate_warnings": duplicate_warnings,
        "total_interactions": len(interactions_found),
        "disclaimer": (
            "⚠️ This interaction check is for informational purposes only. "
            "Do NOT stop or change any prescribed medication based on this result. "
            "Always discuss with your doctor or pharmacist."
        ),
    }
