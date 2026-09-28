from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_patient
from app.models.patient import Patient
from app.models.health_metric import HealthMetric
from app.models.user import User

router = APIRouter()


class MetricCreate(BaseModel):
    metric_name: str
    value: float
    unit: str
    recorded_date: datetime
    notes: Optional[str] = None
    family_member_id: Optional[int] = None


@router.post("/")
def add_metric(
    data: MetricCreate,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    metric = HealthMetric(
        patient_id=patient.id,
        family_member_id=data.family_member_id,
        metric_name=data.metric_name,
        value=data.value,
        unit=data.unit,
        recorded_date=data.recorded_date,
        notes=data.notes,
        source="manual",
    )
    db.add(metric)
    db.commit()
    return {"message": "Metric added", "metric_id": metric.id}


@router.get("/trends")
def get_trends(
    metric_name: Optional[str] = None,
    days: int = 90,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    from datetime import timedelta
    since = datetime.utcnow() - timedelta(days=days)

    query = db.query(HealthMetric).filter(
        HealthMetric.patient_id == patient.id,
        HealthMetric.recorded_date >= since,
    )
    if metric_name:
        query = query.filter(HealthMetric.metric_name.ilike(f"%{metric_name}%"))

    metrics = query.order_by(HealthMetric.recorded_date.asc()).all()

    # Group by metric name
    grouped = {}
    for m in metrics:
        name = m.metric_name
        if name not in grouped:
            grouped[name] = {"name": name, "unit": m.unit, "data": []}
        grouped[name]["data"].append({
            "value": m.value,
            "date": m.recorded_date,
            "notes": m.notes,
        })

    # Add trend direction
    for name, group in grouped.items():
        data = group["data"]
        if len(data) >= 2:
            latest = data[-1]["value"]
            previous = data[-2]["value"]
            if latest > previous:
                group["trend"] = "increasing"
            elif latest < previous:
                group["trend"] = "decreasing"
            else:
                group["trend"] = "stable"
            group["latest_value"] = latest
            group["previous_value"] = previous
        elif data:
            group["trend"] = "stable"
            group["latest_value"] = data[-1]["value"]
            group["previous_value"] = None
        else:
            group["trend"] = "no_data"

    return {
        "trends": list(grouped.values()),
        "disclaimer": (
            "⚠️ These trends are for informational purposes only. "
            "Do not make medical decisions based on this data without consulting your doctor."
        ),
    }


@router.get("/")
def list_metrics(
    metric_name: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    query = db.query(HealthMetric).filter(HealthMetric.patient_id == patient.id)
    if metric_name:
        query = query.filter(HealthMetric.metric_name.ilike(f"%{metric_name}%"))

    metrics = query.order_by(HealthMetric.recorded_date.desc()).limit(limit).all()
    return {
        "metrics": [
            {
                "id": m.id,
                "metric_name": m.metric_name,
                "value": m.value,
                "unit": m.unit,
                "recorded_date": m.recorded_date,
                "source": m.source,
            }
            for m in metrics
        ]
    }
