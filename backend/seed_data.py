"""
seed_data.py — Run this once after starting the backend to populate demo data.

Usage:
    (with venv active, from the backend/ folder)
    python seed_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.patient import Patient, FamilyMember
from app.models.doctor import Doctor
from app.models.medicine import Medicine, DrugInteraction
from app.models.report import MedicalReport, ReportValue
from app.models.reminder import MedicationSchedule
from app.models.appointment import Appointment
from app.models.symptom import Symptom
from app.models.emergency import EmergencyContact
from app.models.notification import Notification
from app.models.health_metric import HealthMetric
from datetime import datetime, timedelta, date
import json

# Ensure all tables exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

def seed():
    print("Seeding MedVision AI demo data...")

    # ── Users ─────────────────────────────────────────────────────────────
    hashed = get_password_hash("Password@123")
    users_data = [
        dict(email="patient@medvision.ai",  full_name="Arun Kumar",              phone="9876543210", role="patient", is_active=True, is_verified=True, preferred_language="en"),
        dict(email="patient2@medvision.ai", full_name="Priya Devi",               phone="9123456789", role="patient", is_active=True, is_verified=True, preferred_language="ta"),
        dict(email="doctor@medvision.ai",   full_name="Dr. Ramesh Venkataraman",  phone="9000000001", role="doctor",  is_active=True, is_verified=True, preferred_language="en"),
        dict(email="doctor2@medvision.ai",  full_name="Dr. Meena Subramaniam",    phone="9000000002", role="doctor",  is_active=True, is_verified=True, preferred_language="ta"),
        dict(email="admin@medvision.ai",    full_name="Admin User",               phone="9000000000", role="admin",   is_active=True, is_verified=True, preferred_language="en"),
    ]
    users = {}
    for ud in users_data:
        existing = db.query(User).filter(User.email == ud["email"]).first()
        if not existing:
            u = User(**ud, hashed_password=hashed)
            db.add(u); db.flush()
            users[ud["email"]] = u
            print(f"  Created user: {ud['email']}")
        else:
            users[ud["email"]] = existing
            print(f"  User exists: {ud['email']}")
    db.commit()

    # ── Patient profiles ──────────────────────────────────────────────────
    p1_user = users["patient@medvision.ai"]
    p2_user = users["patient2@medvision.ai"]

    patient1 = db.query(Patient).filter(Patient.user_id == p1_user.id).first()
    if not patient1:
        patient1 = Patient(user_id=p1_user.id, date_of_birth=date(1990, 5, 15),
            gender="Male", blood_group="O+", height_cm=175, weight_kg=72,
            city="Chennai", state="Tamil Nadu", country="India",
            known_allergies="Penicillin", chronic_conditions="Type 2 Diabetes, Hypertension")
        db.add(patient1); db.flush()

    patient2 = db.query(Patient).filter(Patient.user_id == p2_user.id).first()
    if not patient2:
        patient2 = Patient(user_id=p2_user.id, date_of_birth=date(1985, 11, 22),
            gender="Female", blood_group="A+", height_cm=160, weight_kg=58,
            city="Coimbatore", state="Tamil Nadu", country="India",
            known_allergies="Sulfa drugs", chronic_conditions="Hypothyroidism")
        db.add(patient2); db.flush()
    db.commit()

    # ── Doctor profiles ───────────────────────────────────────────────────
    d1_user = users["doctor@medvision.ai"]
    d2_user = users["doctor2@medvision.ai"]

    if not db.query(Doctor).filter(Doctor.user_id == d1_user.id).first():
        db.add(Doctor(user_id=d1_user.id,
            specialization="General Medicine & Diabetology",
            qualification="MBBS, MD (Internal Medicine)",
            registration_number="TN/2010/12345",
            hospital_name="Apollo Hospitals", city="Chennai",
            years_of_experience=15, consultation_fee=500,
            available_days=json.dumps(["Monday","Tuesday","Wednesday","Thursday","Friday"]),
            available_time_start="09:00", available_time_end="17:00",
            bio="Experienced general physician specializing in diabetes and metabolic disorders.",
            is_verified=True, is_available=True))
        db.flush()

    if not db.query(Doctor).filter(Doctor.user_id == d2_user.id).first():
        db.add(Doctor(user_id=d2_user.id,
            specialization="Cardiology",
            qualification="MBBS, DM (Cardiology)",
            registration_number="TN/2012/67890",
            hospital_name="Fortis Malar Hospital", city="Chennai",
            years_of_experience=12, consultation_fee=800,
            available_days=json.dumps(["Monday","Wednesday","Friday","Saturday"]),
            available_time_start="10:00", available_time_end="16:00",
            bio="Cardiologist with expertise in interventional cardiology.",
            is_verified=True, is_available=True))
        db.flush()
    db.commit()

    # ── Medicines ─────────────────────────────────────────────────────────
    medicines_data = [
        dict(brand_name="Glycomet 500", generic_name="Metformin Hydrochloride", active_ingredient="Metformin",
             drug_category="Antidiabetic", drug_class="Biguanide", is_otc=False, requires_prescription=True,
             general_purpose="Used to treat type 2 diabetes by lowering blood sugar levels.",
             common_precautions="Do not use in severe kidney disease. Avoid alcohol. Monitor kidney function regularly.",
             common_side_effects="Nausea, vomiting, diarrhea, stomach upset (especially when starting treatment).",
             storage_information="Store below 30°C. Keep away from direct sunlight and moisture.",
             important_warnings="Lactic acidosis (rare but serious). Stop before iodine contrast procedures.",
             manufacturer="USV Pvt. Ltd."),
        dict(brand_name="Atorvastatin 10mg", generic_name="Atorvastatin Calcium", active_ingredient="Atorvastatin",
             drug_category="Lipid-lowering", drug_class="Statin", is_otc=False, requires_prescription=True,
             general_purpose="Reduces LDL ('bad') cholesterol and triglycerides, raises HDL ('good') cholesterol.",
             common_precautions="Regular liver function tests recommended. Avoid grapefruit juice.",
             common_side_effects="Muscle pain, weakness, headache, nausea, joint pain.",
             storage_information="Store at room temperature 20-25°C. Keep in original container.",
             important_warnings="Report unexplained muscle pain immediately. May cause liver problems.",
             manufacturer="Sun Pharmaceutical Industries"),
        dict(brand_name="Amlodipine 5mg", generic_name="Amlodipine Besylate", active_ingredient="Amlodipine",
             drug_category="Antihypertensive", drug_class="Calcium Channel Blocker", is_otc=False, requires_prescription=True,
             general_purpose="Treats high blood pressure and chest pain (angina).",
             common_precautions="Do not stop suddenly. Monitor blood pressure regularly.",
             common_side_effects="Swelling of ankles/feet, flushing, headache, dizziness, fatigue.",
             storage_information="Store below 30°C away from light and moisture.",
             important_warnings="Do not stop suddenly without doctor advice.",
             manufacturer="Cipla Ltd."),
        dict(brand_name="Paracetamol 500mg", generic_name="Paracetamol (Acetaminophen)", active_ingredient="Paracetamol",
             drug_category="Analgesic/Antipyretic", drug_class="Analgesic", is_otc=True, requires_prescription=False,
             general_purpose="Relieves mild to moderate pain and reduces fever.",
             common_precautions="Do not exceed recommended dose. Avoid alcohol. Use cautiously in liver disease.",
             common_side_effects="Generally well tolerated. Rare: skin rash, blood disorders.",
             storage_information="Store below 25°C. Keep dry.",
             important_warnings="Overdose can cause serious liver damage.",
             manufacturer="GSK India"),
        dict(brand_name="Aspirin 75mg", generic_name="Aspirin", active_ingredient="Aspirin",
             drug_category="Antiplatelet", drug_class="Antiplatelet/NSAID", is_otc=True, requires_prescription=False,
             general_purpose="Prevents blood clots. Used in heart attack/stroke prevention.",
             common_precautions="Avoid in peptic ulcer. May increase bleeding risk. Not for children under 16.",
             common_side_effects="Stomach irritation, heartburn, nausea. Rarely: stomach bleeding.",
             storage_information="Store below 25°C in a dry place.",
             important_warnings="Increased bleeding risk. Stop before surgery.",
             manufacturer="Bayer Pharmaceuticals"),
        dict(brand_name="Omeprazole 20mg", generic_name="Omeprazole", active_ingredient="Omeprazole",
             drug_category="Proton Pump Inhibitor", drug_class="PPI", is_otc=False, requires_prescription=True,
             general_purpose="Reduces stomach acid. Treats GERD, peptic ulcers, and acid reflux.",
             common_precautions="Long-term use may affect magnesium levels and bone density.",
             common_side_effects="Headache, nausea, diarrhea, stomach pain, constipation.",
             storage_information="Store below 25°C in a dry place.",
             important_warnings="Long-term use may increase risk of fractures.",
             manufacturer="AstraZeneca India"),
        dict(brand_name="Thyroxine 50mcg", generic_name="Levothyroxine Sodium", active_ingredient="Levothyroxine",
             drug_category="Thyroid Hormone", drug_class="Thyroid Hormone", is_otc=False, requires_prescription=True,
             general_purpose="Replaces thyroid hormone in hypothyroidism.",
             common_precautions="Take on empty stomach 30 minutes before food. Regular TSH monitoring required.",
             common_side_effects="Symptoms of over-treatment: palpitations, weight loss, sweating, anxiety.",
             storage_information="Store below 25°C. Protect from light and moisture.",
             important_warnings="Numerous drug interactions. Adjust dose based on regular blood tests.",
             manufacturer="Abbott India Ltd."),
        dict(brand_name="Cetirizine 10mg", generic_name="Cetirizine Hydrochloride", active_ingredient="Cetirizine",
             drug_category="Antihistamine", drug_class="Antihistamine", is_otc=True, requires_prescription=False,
             general_purpose="Treats allergic rhinitis, urticaria (hives), and allergic symptoms.",
             common_precautions="May cause drowsiness. Avoid driving. Caution with alcohol.",
             common_side_effects="Drowsiness, dry mouth, headache, nausea.",
             storage_information="Store at room temperature.",
             important_warnings="Avoid in severe kidney disease. May impair reaction time.",
             manufacturer="UCB India"),
        dict(brand_name="Metoprolol 25mg", generic_name="Metoprolol Succinate", active_ingredient="Metoprolol",
             drug_category="Antihypertensive/Beta-blocker", drug_class="Beta-1 Selective Blocker", is_otc=False, requires_prescription=True,
             general_purpose="Treats high blood pressure, heart failure, and certain heart rhythm problems.",
             common_precautions="Do not stop suddenly. Monitor heart rate and blood pressure.",
             common_side_effects="Fatigue, dizziness, slow heartbeat, cold hands/feet.",
             storage_information="Store below 25°C.",
             important_warnings="Do not stop abruptly – can worsen heart conditions.",
             manufacturer="AstraZeneca India"),
        dict(brand_name="Azithromycin 500mg", generic_name="Azithromycin", active_ingredient="Azithromycin",
             drug_category="Antibiotic", drug_class="Macrolide Antibiotic", is_otc=False, requires_prescription=True,
             general_purpose="Treats bacterial infections including respiratory, skin, and ear infections.",
             common_precautions="Complete the full course. Tell doctor about heart conditions.",
             common_side_effects="Nausea, diarrhea, stomach pain, vomiting.",
             storage_information="Store below 30°C. Keep away from moisture.",
             important_warnings="Not for viral infections (cold/flu). May prolong QT interval.",
             manufacturer="Cipla Ltd."),
    ]
    for md in medicines_data:
        if not db.query(Medicine).filter(Medicine.brand_name == md["brand_name"]).first():
            db.add(Medicine(**md))
    db.commit()
    print(f"  Medicines: {db.query(Medicine).count()} in database")

    # ── Drug Interactions ─────────────────────────────────────────────────
    interactions = [
        dict(drug_a="Metformin", drug_b="Alcohol", interaction_severity="moderate",
             effect="Increased risk of lactic acidosis.",
             mechanism="Both can increase lactic acid levels.",
             recommended_action="Avoid excessive alcohol. Discuss with your doctor.",
             source="MedVision Reference Database"),
        dict(drug_a="Aspirin", drug_b="Warfarin", interaction_severity="major",
             effect="Significantly increased bleeding risk.",
             mechanism="Additive anticoagulant and antiplatelet effects.",
             recommended_action="This combination requires close medical supervision.",
             source="MedVision Reference Database"),
        dict(drug_a="Atorvastatin", drug_b="Azithromycin", interaction_severity="moderate",
             effect="Increased risk of myopathy (muscle damage).",
             mechanism="Azithromycin inhibits CYP3A4, increasing Atorvastatin levels.",
             recommended_action="Monitor for muscle pain. Discuss with your doctor.",
             source="MedVision Reference Database"),
        dict(drug_a="Omeprazole", drug_b="Levothyroxine", interaction_severity="moderate",
             effect="Reduced thyroid hormone efficacy.",
             mechanism="Omeprazole reduces absorption of Levothyroxine.",
             recommended_action="Take Levothyroxine at least 4 hours before Omeprazole. Monitor TSH levels.",
             source="MedVision Reference Database"),
        dict(drug_a="Amlodipine", drug_b="Metoprolol", interaction_severity="minor",
             effect="May cause excessive blood pressure lowering.",
             mechanism="Additive blood pressure lowering effect.",
             recommended_action="Monitor blood pressure regularly. Sometimes used intentionally.",
             source="MedVision Reference Database"),
    ]
    for ix in interactions:
        exists = db.query(DrugInteraction).filter(
            DrugInteraction.drug_a == ix["drug_a"],
            DrugInteraction.drug_b == ix["drug_b"]
        ).first()
        if not exists:
            db.add(DrugInteraction(**ix))
    db.commit()
    print(f"  Drug interactions: {db.query(DrugInteraction).count()} in database")

    # ── Medical Reports for patient1 ──────────────────────────────────────
    if db.query(MedicalReport).filter(MedicalReport.patient_id == patient1.id).count() == 0:
        now = datetime.utcnow()

        # Latest report
        report1 = MedicalReport(
            patient_id=patient1.id, report_type="blood_test",
            report_date=now - timedelta(days=30), lab_name="City Diagnostics",
            doctor_name="Dr. Ramesh Venkataraman", file_type="pdf",
            original_filename="blood_report_aug2026.pdf", ocr_confidence=0.88,
            summary="Report contains 9 test results. 2 values outside normal range (Hemoglobin, LDL Cholesterol). 3 values need attention (Fasting Blood Sugar, HbA1c, Total Cholesterol, HDL Cholesterol). 3 normal.",
            is_ocr_verified=True
        )
        db.add(report1); db.flush()

        values1 = [
            ("Hemoglobin",          "11.2", "g/dL",  "13.0 - 17.0",   "abnormal"),
            ("WBC Count",           "8500", "/cumm",  "4000 - 11000",  "normal"),
            ("Platelet Count",      "180000", "/cumm", "150000 - 400000", "normal"),
            ("Fasting Blood Sugar", "126",  "mg/dL", "70 - 100",      "attention"),
            ("HbA1c",               "7.2",  "%",     "< 5.7",         "attention"),
            ("Total Cholesterol",   "215",  "mg/dL", "< 200",         "attention"),
            ("LDL Cholesterol",     "145",  "mg/dL", "< 100",         "abnormal"),
            ("HDL Cholesterol",     "38",   "mg/dL", "> 40",          "attention"),
            ("Serum Creatinine",    "1.1",  "mg/dL", "0.6 - 1.2",    "normal"),
        ]
        for test_name, result, unit, ref, status in values1:
            db.add(ReportValue(report_id=report1.id, test_name=test_name, result=result,
                               unit=unit, reference_range_text=ref, status=status))
            db.add(HealthMetric(patient_id=patient1.id, metric_name=test_name, value=float(result.replace(",", "")),
                                unit=unit, recorded_date=now - timedelta(days=30), source="report", report_id=report1.id))

        # Older report for trend comparison
        report2 = MedicalReport(
            patient_id=patient1.id, report_type="blood_test",
            report_date=now - timedelta(days=120), lab_name="City Diagnostics",
            ocr_confidence=0.85, is_ocr_verified=True,
            summary="Previous report – 4 months ago."
        )
        db.add(report2); db.flush()

        older_values = [
            ("Hemoglobin",          "11.8", "g/dL",  "13.0 - 17.0", "abnormal"),
            ("Fasting Blood Sugar", "138",  "mg/dL", "70 - 100",    "abnormal"),
            ("HbA1c",               "7.8",  "%",     "< 5.7",       "abnormal"),
            ("Total Cholesterol",   "230",  "mg/dL", "< 200",       "abnormal"),
            ("LDL Cholesterol",     "160",  "mg/dL", "< 100",       "abnormal"),
        ]
        for test_name, result, unit, ref, status in older_values:
            db.add(ReportValue(report_id=report2.id, test_name=test_name, result=result,
                               unit=unit, reference_range_text=ref, status=status))
            db.add(HealthMetric(patient_id=patient1.id, metric_name=test_name, value=float(result),
                                unit=unit, recorded_date=now - timedelta(days=120), source="report", report_id=report2.id))

        db.commit()
        print(f"  Medical reports created for patient1")

    # ── Medication Schedules ──────────────────────────────────────────────
    if db.query(MedicationSchedule).filter(MedicationSchedule.patient_id == patient1.id).count() == 0:
        today = date.today()
        schedules = [
            dict(patient_id=patient1.id, medicine_name="Glycomet 500", strength="500mg",
                 frequency="twice_daily", times=json.dumps(["08:00","20:00"]),
                 start_date=today - timedelta(days=30), end_date=today + timedelta(days=60),
                 instructions="Monitor blood sugar regularly", before_after_food="after food", is_active=True),
            dict(patient_id=patient1.id, medicine_name="Atorvastatin 10mg", strength="10mg",
                 frequency="once_daily_night", times=json.dumps(["21:00"]),
                 start_date=today - timedelta(days=30), end_date=today + timedelta(days=60),
                 instructions="At night", before_after_food="after food", is_active=True),
            dict(patient_id=patient1.id, medicine_name="Aspirin 75mg", strength="75mg",
                 frequency="once_daily_morning", times=json.dumps(["07:00"]),
                 start_date=today - timedelta(days=30),
                 instructions="With water", before_after_food="after food", is_active=True),
        ]
        for s in schedules:
            db.add(MedicationSchedule(**s))
        db.commit()
        print("  Medication schedules created")

    # ── Symptoms ──────────────────────────────────────────────────────────
    if db.query(Symptom).filter(Symptom.patient_id == patient1.id).count() == 0:
        db.add(Symptom(patient_id=patient1.id, description="Mild headache and fatigue", duration="3 days", severity="mild", language="en"))
        db.add(Symptom(patient_id=patient1.id, description="Increased thirst and frequent urination", duration="1 week", severity="moderate", language="en"))
        db.commit()
        print("  Symptoms created")

    # ── Emergency Contact ─────────────────────────────────────────────────
    if db.query(EmergencyContact).filter(EmergencyContact.patient_id == patient1.id).count() == 0:
        db.add(EmergencyContact(patient_id=patient1.id, name="Sujatha Kumar", relation="Spouse", phone="9876500000", is_primary=True))
        db.commit()

    # ── Family Member ─────────────────────────────────────────────────────
    if db.query(FamilyMember).filter(FamilyMember.patient_id == patient1.id).count() == 0:
        db.add(FamilyMember(patient_id=patient1.id, name="Kavitha Kumar", relation="Spouse", date_of_birth=date(1992, 3, 10), gender="Female", blood_group="B+"))
        db.commit()

    # ── Appointment ───────────────────────────────────────────────────────
    doctor1 = db.query(Doctor).filter(Doctor.user_id == users["doctor@medvision.ai"].id).first()
    if doctor1 and db.query(Appointment).filter(Appointment.patient_id == patient1.id).count() == 0:
        db.add(Appointment(patient_id=patient1.id, doctor_id=doctor1.id,
            appointment_date=datetime.utcnow() + timedelta(days=3),
            reason="Follow-up for diabetes management", status="confirmed"))
        db.commit()

    # ── Notifications ─────────────────────────────────────────────────────
    if db.query(Notification).filter(Notification.user_id == p1_user.id).count() == 0:
        db.add(Notification(user_id=p1_user.id, title="Report Analysis Complete",
            message="Your blood report from City Diagnostics has been analyzed. 3 values need attention.",
            notification_type="report", is_read=False))
        db.add(Notification(user_id=p1_user.id, title="Medicine Reminder",
            message="Time to take Glycomet 500mg (after food).",
            notification_type="reminder", is_read=False))
        db.commit()

    db.close()
    print("\n✅ Seed complete! Demo accounts:")
    print("   patient@medvision.ai  / Password@123")
    print("   doctor@medvision.ai   / Password@123")
    print("   admin@medvision.ai    / Password@123")


if __name__ == "__main__":
    seed()
