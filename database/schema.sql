-- ============================================================
-- MedVision AI – PostgreSQL Database Schema
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(20) DEFAULT 'patient' CHECK (role IN ('patient','doctor','admin')),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    profile_image VARCHAR(500),
    preferred_language VARCHAR(10) DEFAULT 'en',
    dark_mode BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    last_login TIMESTAMPTZ
);

-- Patients
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    date_of_birth DATE,
    gender VARCHAR(20),
    blood_group VARCHAR(10),
    height_cm FLOAT,
    weight_kg FLOAT,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100) DEFAULT 'India',
    pincode VARCHAR(10),
    occupation VARCHAR(100),
    marital_status VARCHAR(30),
    known_allergies TEXT,
    chronic_conditions TEXT,
    current_medications TEXT,
    family_medical_history TEXT,
    insurance_provider VARCHAR(200),
    insurance_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Doctors
CREATE TABLE IF NOT EXISTS doctors (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    specialization VARCHAR(200),
    qualification VARCHAR(500),
    registration_number VARCHAR(100) UNIQUE,
    hospital_name VARCHAR(300),
    hospital_address TEXT,
    city VARCHAR(100),
    years_of_experience INTEGER DEFAULT 0,
    consultation_fee FLOAT DEFAULT 0,
    available_days VARCHAR(200),
    available_time_start VARCHAR(10),
    available_time_end VARCHAR(10),
    bio TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Family Members
CREATE TABLE IF NOT EXISTS family_members (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    relationship VARCHAR(50),
    date_of_birth DATE,
    gender VARCHAR(20),
    blood_group VARCHAR(10),
    known_allergies TEXT,
    chronic_conditions TEXT,
    current_medications TEXT,
    profile_image VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Symptoms
CREATE TABLE IF NOT EXISTS symptoms (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    family_member_id INTEGER REFERENCES family_members(id) ON DELETE SET NULL,
    description TEXT NOT NULL,
    input_method VARCHAR(20) DEFAULT 'text',
    voice_transcript TEXT,
    duration VARCHAR(100),
    severity VARCHAR(20),
    location_on_body VARCHAR(200),
    language VARCHAR(10) DEFAULT 'en',
    is_emergency_flagged BOOLEAN DEFAULT FALSE,
    emergency_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Medical Reports
CREATE TABLE IF NOT EXISTS medical_reports (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    family_member_id INTEGER REFERENCES family_members(id) ON DELETE SET NULL,
    report_type VARCHAR(100),
    report_date TIMESTAMPTZ,
    lab_name VARCHAR(300),
    doctor_name VARCHAR(300),
    file_path VARCHAR(500),
    file_type VARCHAR(20),
    original_filename VARCHAR(500),
    ocr_raw_text TEXT,
    ocr_confidence FLOAT,
    is_ocr_verified BOOLEAN DEFAULT FALSE,
    ai_explanation TEXT,
    ai_explanation_tamil TEXT,
    ai_questions_for_doctor TEXT,
    summary TEXT,
    is_doctor_reviewed BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Report Values
CREATE TABLE IF NOT EXISTS report_values (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES medical_reports(id) ON DELETE CASCADE,
    test_name VARCHAR(300) NOT NULL,
    result VARCHAR(100),
    unit VARCHAR(50),
    reference_range_low FLOAT,
    reference_range_high FLOAT,
    reference_range_text VARCHAR(200),
    status VARCHAR(20),
    explanation TEXT,
    explanation_tamil TEXT,
    is_manually_corrected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Medicines
CREATE TABLE IF NOT EXISTS medicines (
    id SERIAL PRIMARY KEY,
    brand_name VARCHAR(300) NOT NULL,
    generic_name VARCHAR(300),
    active_ingredient VARCHAR(300),
    drug_category VARCHAR(200),
    general_purpose TEXT,
    common_precautions TEXT,
    common_side_effects TEXT,
    storage_information TEXT,
    important_warnings TEXT,
    manufacturer VARCHAR(300),
    drug_class VARCHAR(200),
    is_otc BOOLEAN DEFAULT FALSE,
    is_controlled BOOLEAN DEFAULT FALSE,
    requires_prescription BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT TRUE,
    source VARCHAR(200) DEFAULT 'MedVision Medicine Database',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Drug Interactions
CREATE TABLE IF NOT EXISTS drug_interactions (
    id SERIAL PRIMARY KEY,
    drug_a VARCHAR(300) NOT NULL,
    drug_b VARCHAR(300) NOT NULL,
    interaction_severity VARCHAR(50),
    mechanism TEXT,
    effect TEXT,
    clinical_significance TEXT,
    recommended_action TEXT,
    source VARCHAR(300),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Prescriptions
CREATE TABLE IF NOT EXISTS prescriptions (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    family_member_id INTEGER REFERENCES family_members(id) ON DELETE SET NULL,
    doctor_id INTEGER REFERENCES doctors(id) ON DELETE SET NULL,
    file_path VARCHAR(500),
    original_filename VARCHAR(500),
    ocr_raw_text TEXT,
    ocr_confidence FLOAT,
    prescription_date TIMESTAMPTZ,
    is_user_verified BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Prescription Items
CREATE TABLE IF NOT EXISTS prescription_items (
    id SERIAL PRIMARY KEY,
    prescription_id INTEGER REFERENCES prescriptions(id) ON DELETE CASCADE,
    medicine_name VARCHAR(300),
    strength VARCHAR(100),
    dosage_instruction VARCHAR(300),
    frequency VARCHAR(100),
    duration VARCHAR(100),
    before_after_food VARCHAR(50),
    doctor_notes TEXT,
    ocr_confidence FLOAT,
    needs_verification BOOLEAN DEFAULT FALSE,
    is_user_confirmed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Medication Schedules (Reminders)
CREATE TABLE IF NOT EXISTS medication_schedules (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    family_member_id INTEGER REFERENCES family_members(id) ON DELETE SET NULL,
    medicine_name VARCHAR(300) NOT NULL,
    strength VARCHAR(100),
    frequency VARCHAR(100),
    times VARCHAR(500),
    start_date DATE NOT NULL,
    end_date DATE,
    instructions TEXT,
    before_after_food VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Medication Logs
CREATE TABLE IF NOT EXISTS medication_logs (
    id SERIAL PRIMARY KEY,
    schedule_id INTEGER REFERENCES medication_schedules(id) ON DELETE CASCADE,
    scheduled_time TIMESTAMPTZ NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    taken_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Pharmacy Bills
CREATE TABLE IF NOT EXISTS pharmacy_bills (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    file_path VARCHAR(500),
    original_filename VARCHAR(500),
    pharmacy_name VARCHAR(300),
    bill_date TIMESTAMPTZ,
    total_amount FLOAT DEFAULT 0,
    ocr_raw_text TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Pharmacy Bill Items
CREATE TABLE IF NOT EXISTS pharmacy_bill_items (
    id SERIAL PRIMARY KEY,
    bill_id INTEGER REFERENCES pharmacy_bills(id) ON DELETE CASCADE,
    medicine_name VARCHAR(300),
    quantity VARCHAR(50),
    unit_price FLOAT,
    total_price FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Appointments
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    family_member_id INTEGER REFERENCES family_members(id) ON DELETE SET NULL,
    doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE,
    appointment_date TIMESTAMPTZ NOT NULL,
    reason TEXT,
    status VARCHAR(30) DEFAULT 'requested',
    notes TEXT,
    follow_up_date TIMESTAMPTZ,
    is_reminder_sent BOOLEAN DEFAULT FALSE,
    patient_rating INTEGER,
    patient_feedback TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Doctor Notes
CREATE TABLE IF NOT EXISTS doctor_notes (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    report_id INTEGER REFERENCES medical_reports(id) ON DELETE SET NULL,
    appointment_id INTEGER REFERENCES appointments(id) ON DELETE SET NULL,
    note_text TEXT NOT NULL,
    follow_up_date TIMESTAMPTZ,
    is_approved_summary BOOLEAN DEFAULT FALSE,
    approved_summary_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Health Metrics
CREATE TABLE IF NOT EXISTS health_metrics (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    family_member_id INTEGER REFERENCES family_members(id) ON DELETE SET NULL,
    metric_name VARCHAR(200) NOT NULL,
    value FLOAT NOT NULL,
    unit VARCHAR(50),
    recorded_date TIMESTAMPTZ NOT NULL,
    source VARCHAR(100) DEFAULT 'manual',
    report_id INTEGER REFERENCES medical_reports(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Emergency Contacts
CREATE TABLE IF NOT EXISTS emergency_contacts (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    relationship VARCHAR(100),
    phone VARCHAR(20) NOT NULL,
    alternate_phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Documents (Medical Locker)
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    family_member_id INTEGER REFERENCES family_members(id) ON DELETE SET NULL,
    category VARCHAR(100),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    file_path VARCHAR(500) NOT NULL,
    original_filename VARCHAR(500),
    file_type VARCHAR(20),
    file_size_kb INTEGER,
    document_date TIMESTAMPTZ,
    tags VARCHAR(500),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50),
    reference_id INTEGER,
    reference_type VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chatbot History
CREATE TABLE IF NOT EXISTS chatbot_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(100),
    role VARCHAR(20),
    message TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    input_method VARCHAR(20) DEFAULT 'text',
    is_ai_response BOOLEAN DEFAULT FALSE,
    ai_confidence FLOAT,
    has_disclaimer BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(200) NOT NULL,
    entity_type VARCHAR(100),
    entity_id INTEGER,
    details TEXT,
    ip_address VARCHAR(50),
    user_agent VARCHAR(500),
    status VARCHAR(20) DEFAULT 'success',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_patients_user_id ON patients(user_id);
CREATE INDEX IF NOT EXISTS idx_medical_reports_patient_id ON medical_reports(patient_id);
CREATE INDEX IF NOT EXISTS idx_report_values_report_id ON report_values(report_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_patient_id ON prescriptions(patient_id);
CREATE INDEX IF NOT EXISTS idx_medication_schedules_patient_id ON medication_schedules(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_patient_id ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor_id ON appointments(doctor_id);
CREATE INDEX IF NOT EXISTS idx_health_metrics_patient_id ON health_metrics(patient_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_chatbot_history_user_id ON chatbot_history(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_medicines_brand_name ON medicines(brand_name);
CREATE INDEX IF NOT EXISTS idx_medicines_generic_name ON medicines(generic_name);
