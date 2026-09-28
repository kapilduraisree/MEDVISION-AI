"""
MedVision AI – Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

from app.core.config import settings
from app.core.database import engine, Base
from app.api.routes import (
    auth,
    users,
    patients,
    doctors,
    admin,
    reports,
    prescriptions,
    medicines,
    drug_interactions,
    reminders,
    pharmacy_bills,
    appointments,
    chatbot,
    health_metrics,
    documents,
    family,
    emergency,
    notifications,
    symptoms,
    ai_summary,
    voice,
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MedVision AI API",
    description=(
        "Multimodal AI-Based Medicine & Health Report Analysis System. "
        "All AI-generated content is informational only and must be reviewed "
        "by a qualified healthcare professional before clinical use."
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Routers
prefix = "/api/v1"
app.include_router(auth.router, prefix=prefix + "/auth", tags=["Authentication"])
app.include_router(users.router, prefix=prefix + "/users", tags=["Users"])
app.include_router(patients.router, prefix=prefix + "/patients", tags=["Patients"])
app.include_router(doctors.router, prefix=prefix + "/doctors", tags=["Doctors"])
app.include_router(admin.router, prefix=prefix + "/admin", tags=["Admin"])
app.include_router(reports.router, prefix=prefix + "/reports", tags=["Medical Reports"])
app.include_router(prescriptions.router, prefix=prefix + "/prescriptions", tags=["Prescriptions"])
app.include_router(medicines.router, prefix=prefix + "/medicines", tags=["Medicines"])
app.include_router(drug_interactions.router, prefix=prefix + "/drug-interactions", tags=["Drug Interactions"])
app.include_router(reminders.router, prefix=prefix + "/reminders", tags=["Medicine Reminders"])
app.include_router(pharmacy_bills.router, prefix=prefix + "/pharmacy-bills", tags=["Pharmacy Bills"])
app.include_router(appointments.router, prefix=prefix + "/appointments", tags=["Appointments"])
app.include_router(chatbot.router, prefix=prefix + "/chatbot", tags=["AI Chatbot"])
app.include_router(health_metrics.router, prefix=prefix + "/health-metrics", tags=["Health Metrics"])
app.include_router(documents.router, prefix=prefix + "/documents", tags=["Medical Locker"])
app.include_router(family.router, prefix=prefix + "/family", tags=["Family Profiles"])
app.include_router(emergency.router, prefix=prefix + "/emergency", tags=["Emergency"])
app.include_router(notifications.router, prefix=prefix + "/notifications", tags=["Notifications"])
app.include_router(symptoms.router, prefix=prefix + "/symptoms", tags=["Symptoms"])
app.include_router(ai_summary.router, prefix=prefix + "/ai-summary", tags=["AI Summary"])
app.include_router(voice.router, prefix=prefix + "/voice", tags=["Voice"])


@app.get("/", include_in_schema=False)
def root():
    return JSONResponse({
        "app": "MedVision AI",
        "version": "1.0.0",
        "status": "running",
        "disclaimer": (
            "This system provides informational content only. "
            "All medical information must be verified by a qualified healthcare professional."
        ),
    })


@app.get("/health", include_in_schema=False)
def health_check():
    return {"status": "healthy"}
