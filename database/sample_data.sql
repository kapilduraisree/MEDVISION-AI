-- ============================================================
-- MedVision AI – Sample Data for Demo
-- Passwords are bcrypt hashes of "Password@123"
-- ============================================================

-- Sample Users
INSERT INTO users (email, hashed_password, full_name, phone, role, is_active, is_verified, preferred_language)
VALUES
  ('patient@medvision.ai',  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMUdfpMm6VdH8Iz3VUb3lGZ.q6', 'Arun Kumar', '9876543210', 'patient', TRUE, TRUE, 'en'),
  ('patient2@medvision.ai', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMUdfpMm6VdH8Iz3VUb3lGZ.q6', 'Priya Devi',  '9123456789', 'patient', TRUE, TRUE, 'ta'),
  ('doctor@medvision.ai',   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMUdfpMm6VdH8Iz3VUb3lGZ.q6', 'Dr. Ramesh Venkataraman', '9000000001', 'doctor', TRUE, TRUE, 'en'),
  ('doctor2@medvision.ai',  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMUdfpMm6VdH8Iz3VUb3lGZ.q6', 'Dr. Meena Subramaniam',   '9000000002', 'doctor', TRUE, TRUE, 'ta'),
  ('admin@medvision.ai',    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMUdfpMm6VdH8Iz3VUb3lGZ.q6', 'Admin User',  '9000000000', 'admin',  TRUE, TRUE, 'en')
ON CONFLICT (email) DO NOTHING;

-- Patient Profiles
INSERT INTO patients (user_id, date_of_birth, gender, blood_group, height_cm, weight_kg, city, state, country, known_allergies, chronic_conditions)
SELECT id, '1990-05-15', 'Male', 'O+', 175, 72, 'Chennai', 'Tamil Nadu', 'India',
       'Penicillin', 'Type 2 Diabetes, Hypertension'
FROM users WHERE email = 'patient@medvision.ai'
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO patients (user_id, date_of_birth, gender, blood_group, height_cm, weight_kg, city, state, country, known_allergies, chronic_conditions)
SELECT id, '1985-11-22', 'Female', 'A+', 160, 58, 'Coimbatore', 'Tamil Nadu', 'India',
       'Sulfa drugs', 'Hypothyroidism'
FROM users WHERE email = 'patient2@medvision.ai'
ON CONFLICT (user_id) DO NOTHING;

-- Doctor Profiles
INSERT INTO doctors (user_id, specialization, qualification, registration_number, hospital_name, hospital_address, city, years_of_experience, consultation_fee, available_days, available_time_start, available_time_end, bio, is_verified, is_available)
SELECT id, 'General Medicine & Diabetology', 'MBBS, MD (Internal Medicine)', 'TN/2010/12345',
       'Apollo Hospitals', '21 Greams Lane, Thousand Lights, Chennai', 'Chennai',
       15, 500, '["Monday","Tuesday","Wednesday","Thursday","Friday"]', '09:00', '17:00',
       'Experienced general physician with 15 years specializing in diabetes and metabolic disorders.',
       TRUE, TRUE
FROM users WHERE email = 'doctor@medvision.ai'
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO doctors (user_id, specialization, qualification, registration_number, hospital_name, hospital_address, city, years_of_experience, consultation_fee, available_days, available_time_start, available_time_end, bio, is_verified, is_available)
SELECT id, 'Cardiology', 'MBBS, DM (Cardiology)', 'TN/2012/67890',
       'Fortis Malar Hospital', 'No.52, 1st Main Road, Gandhi Nagar, Adyar, Chennai', 'Chennai',
       12, 800, '["Monday","Wednesday","Friday","Saturday"]', '10:00', '16:00',
       'Cardiologist with expertise in interventional cardiology and heart failure management.',
       TRUE, TRUE
FROM users WHERE email = 'doctor2@medvision.ai'
ON CONFLICT (user_id) DO NOTHING;

-- Medicines Database
INSERT INTO medicines (brand_name, generic_name, active_ingredient, drug_category, general_purpose, common_precautions, common_side_effects, storage_information, important_warnings, manufacturer, drug_class, is_otc, requires_prescription)
VALUES
  ('Glycomet 500', 'Metformin Hydrochloride', 'Metformin', 'Antidiabetic',
   'Used to treat type 2 diabetes by lowering blood sugar levels.',
   'Do not use in severe kidney disease. Avoid alcohol. Monitor kidney function regularly.',
   'Nausea, vomiting, diarrhea, stomach upset (especially when starting treatment).',
   'Store below 30°C. Keep away from direct sunlight and moisture.',
   'Lactic acidosis (rare but serious). Stop before iodine contrast procedures.',
   'USV Pvt. Ltd.', 'Biguanide', FALSE, TRUE),

  ('Atorvastatin 10mg', 'Atorvastatin Calcium', 'Atorvastatin', 'Lipid-lowering',
   'Reduces LDL ("bad") cholesterol and triglycerides, raises HDL ("good") cholesterol.',
   'Regular liver function tests recommended. Avoid grapefruit juice.',
   'Muscle pain, weakness, headache, nausea, joint pain.',
   'Store at room temperature 20–25°C. Keep in original container.',
   'Report unexplained muscle pain immediately. May cause liver problems.',
   'Sun Pharmaceutical Industries', 'Statin', FALSE, TRUE),

  ('Amlodipine 5mg', 'Amlodipine Besylate', 'Amlodipine', 'Antihypertensive',
   'Treats high blood pressure and chest pain (angina).',
   'Do not stop suddenly. Monitor blood pressure regularly. Use cautiously in liver disease.',
   'Swelling of ankles/feet, flushing, headache, dizziness, fatigue.',
   'Store below 30°C away from light and moisture.',
   'Do not stop suddenly without doctor advice.',
   'Cipla Ltd.', 'Calcium Channel Blocker', FALSE, TRUE),

  ('Paracetamol 500mg', 'Paracetamol (Acetaminophen)', 'Paracetamol', 'Analgesic/Antipyretic',
   'Relieves mild to moderate pain and reduces fever.',
   'Do not exceed recommended dose. Avoid alcohol. Use cautiously in liver disease.',
   'Generally well tolerated. Rare: skin rash, blood disorders.',
   'Store below 25°C. Keep dry.',
   'Overdose can cause serious liver damage. Do not combine with other paracetamol products.',
   'GSK India', 'Analgesic', TRUE, FALSE),

  ('Azithromycin 500mg', 'Azithromycin', 'Azithromycin', 'Antibiotic',
   'Treats bacterial infections including respiratory, skin, and ear infections.',
   'Complete the full course. Tell doctor about heart conditions. Check for drug interactions.',
   'Nausea, diarrhea, stomach pain, vomiting.',
   'Store below 30°C. Keep away from moisture.',
   'Not for viral infections (cold/flu). May prolong QT interval in heart patients.',
   'Cipla Ltd.', 'Macrolide Antibiotic', FALSE, TRUE),

  ('Omeprazole 20mg', 'Omeprazole', 'Omeprazole', 'Proton Pump Inhibitor',
   'Reduces stomach acid. Treats GERD, peptic ulcers, and acid reflux.',
   'Long-term use may affect magnesium levels and bone density.',
   'Headache, nausea, diarrhea, stomach pain, constipation.',
   'Store below 25°C in a dry place.',
   'Long-term use may increase risk of fractures and Clostridium difficile infection.',
   'AstraZeneca India', 'PPI', FALSE, TRUE),

  ('Thyroxine 50mcg', 'Levothyroxine Sodium', 'Levothyroxine', 'Thyroid Hormone',
   'Replaces thyroid hormone in hypothyroidism.',
   'Take on empty stomach 30 minutes before food. Regular TSH monitoring required.',
   'Symptoms of over-treatment: palpitations, weight loss, sweating, anxiety.',
   'Store below 25°C. Protect from light and moisture.',
   'Numerous drug interactions. Adjust dose based on regular blood tests.',
   'Abbott India Ltd.', 'Thyroid Hormone', FALSE, TRUE),

  ('Aspirin 75mg', 'Aspirin (Acetylsalicylic Acid)', 'Aspirin', 'Antiplatelet',
   'Prevents blood clots. Used in heart attack/stroke prevention.',
   'Avoid in peptic ulcer. May increase bleeding risk. Not for children under 16.',
   'Stomach irritation, heartburn, nausea. Rarely: stomach bleeding.',
   'Store below 25°C in a dry place.',
   'Increased bleeding risk. Stop before surgery. Not for children with viral illness.',
   'Bayer Pharmaceuticals', 'Antiplatelet/NSAID', TRUE, FALSE),

  ('Cetirizine 10mg', 'Cetirizine Hydrochloride', 'Cetirizine', 'Antihistamine',
   'Treats allergic rhinitis, urticaria (hives), and allergic symptoms.',
   'May cause drowsiness. Avoid driving. Caution with alcohol.',
   'Drowsiness, dry mouth, headache, nausea.',
   'Store at room temperature.',
   'Avoid in severe kidney disease. May impair reaction time.',
   'UCB India', 'Antihistamine', TRUE, FALSE),

  ('Metoprolol 25mg', 'Metoprolol Succinate', 'Metoprolol', 'Antihypertensive/Beta-blocker',
   'Treats high blood pressure, heart failure, and certain heart rhythm problems.',
   'Do not stop suddenly. Monitor heart rate and blood pressure.',
   'Fatigue, dizziness, slow heartbeat, cold hands/feet.',
   'Store below 25°C.',
   'Do not stop abruptly – can worsen heart conditions. Mask symptoms of low blood sugar.',
   'AstraZeneca India', 'Beta-1 Selective Blocker', FALSE, TRUE)
ON CONFLICT DO NOTHING;

-- Drug Interactions
INSERT INTO drug_interactions (drug_a, drug_b, interaction_severity, mechanism, effect, clinical_significance, recommended_action, source)
VALUES
  ('Metformin', 'Alcohol', 'moderate',
   'Both can increase lactic acid levels.',
   'Increased risk of lactic acidosis.',
   'Moderate clinical significance.',
   'Avoid excessive alcohol consumption while on Metformin. Discuss with your doctor.',
   'MedVision Reference Database'),

  ('Aspirin', 'Warfarin', 'major',
   'Additive anticoagulant and antiplatelet effects.',
   'Significantly increased bleeding risk.',
   'High clinical significance.',
   'This combination requires close medical supervision. Do not start/stop without doctor guidance.',
   'MedVision Reference Database'),

  ('Atorvastatin', 'Azithromycin', 'moderate',
   'Azithromycin inhibits CYP3A4, increasing Atorvastatin levels.',
   'Increased risk of myopathy (muscle damage).',
   'Moderate clinical significance.',
   'Monitor for muscle pain. Discuss with your doctor about temporary statin dose adjustment.',
   'MedVision Reference Database'),

  ('Amlodipine', 'Metoprolol', 'minor',
   'Additive blood pressure lowering effect.',
   'May cause excessive blood pressure lowering.',
   'Minor clinical significance with monitoring.',
   'Monitor blood pressure regularly. This combination is sometimes used intentionally.',
   'MedVision Reference Database'),

  ('Omeprazole', 'Metformin', 'minor',
   'Omeprazole may slightly increase Metformin levels.',
   'Possible minor increase in Metformin effects.',
   'Minor clinical significance.',
   'Generally safe combination. Routine monitoring is adequate.',
   'MedVision Reference Database'),

  ('Thyroxine', 'Omeprazole', 'moderate',
   'Omeprazole reduces absorption of Levothyroxine.',
   'Reduced thyroid hormone efficacy.',
   'Moderate significance, especially in hypothyroid patients.',
   'Take Levothyroxine at least 4 hours before Omeprazole. Monitor TSH levels.',
   'MedVision Reference Database'),

  ('Aspirin', 'Metoprolol', 'minor',
   'NSAIDs may reduce antihypertensive effects of beta-blockers.',
   'Possible reduced blood pressure control.',
   'Minor significance.',
   'Monitor blood pressure. Use lowest effective aspirin dose.',
   'MedVision Reference Database')
ON CONFLICT DO NOTHING;

-- Sample Medical Report (for patient 1)
DO $$
DECLARE
  v_patient_id INTEGER;
  v_report_id  INTEGER;
BEGIN
  SELECT id INTO v_patient_id FROM patients WHERE user_id = (SELECT id FROM users WHERE email = 'patient@medvision.ai');

  IF v_patient_id IS NOT NULL THEN
    INSERT INTO medical_reports (patient_id, report_type, report_date, lab_name, doctor_name,
      file_path, file_type, original_filename, ocr_confidence, summary, is_ocr_verified)
    VALUES (v_patient_id, 'blood_test', NOW() - INTERVAL '30 days', 'City Diagnostics', 'Dr. Ramesh Venkataraman',
      '/uploads/reports/sample_blood_report.pdf', 'pdf', 'blood_report_sep2026.pdf',
      0.88,
      'This report contains 7 test results. 2 values within normal range. 3 values need attention: Fasting Blood Sugar, HbA1c, LDL Cholesterol. 2 values are outside normal range: Hemoglobin, HDL Cholesterol.',
      TRUE)
    RETURNING id INTO v_report_id;

    -- Report Values
    INSERT INTO report_values (report_id, test_name, result, unit, reference_range_text, status)
    VALUES
      (v_report_id, 'Hemoglobin',       '11.2', 'g/dL',  '13.0 - 17.0',  'abnormal'),
      (v_report_id, 'WBC Count',        '8500', '/cumm', '4000 - 11000', 'normal'),
      (v_report_id, 'Platelet Count',   '180000', '/cumm', '150000 - 400000', 'normal'),
      (v_report_id, 'Fasting Blood Sugar', '126', 'mg/dL', '70 - 100',   'attention'),
      (v_report_id, 'HbA1c',            '7.2',  '%',     '< 5.7',        'attention'),
      (v_report_id, 'Total Cholesterol','215',  'mg/dL', '< 200',        'attention'),
      (v_report_id, 'LDL Cholesterol',  '145',  'mg/dL', '< 100',        'abnormal'),
      (v_report_id, 'HDL Cholesterol',  '38',   'mg/dL', '> 40',         'attention'),
      (v_report_id, 'Serum Creatinine', '1.1',  'mg/dL', '0.6 - 1.2',   'normal');

    -- Health Metrics from report
    INSERT INTO health_metrics (patient_id, metric_name, value, unit, recorded_date, source, report_id)
    VALUES
      (v_patient_id, 'Hemoglobin', 11.2, 'g/dL', NOW() - INTERVAL '30 days', 'report', v_report_id),
      (v_patient_id, 'Fasting Blood Sugar', 126, 'mg/dL', NOW() - INTERVAL '30 days', 'report', v_report_id),
      (v_patient_id, 'HbA1c', 7.2, '%', NOW() - INTERVAL '30 days', 'report', v_report_id),
      (v_patient_id, 'Total Cholesterol', 215, 'mg/dL', NOW() - INTERVAL '30 days', 'report', v_report_id),
      (v_patient_id, 'LDL Cholesterol', 145, 'mg/dL', NOW() - INTERVAL '30 days', 'report', v_report_id);

    -- Older report for trending
    INSERT INTO medical_reports (patient_id, report_type, report_date, lab_name, doctor_name, ocr_confidence, summary, is_ocr_verified)
    VALUES (v_patient_id, 'blood_test', NOW() - INTERVAL '120 days', 'City Diagnostics', 'Dr. Ramesh Venkataraman',
      0.85, 'Previous report – 4 months ago.', TRUE)
    RETURNING id INTO v_report_id;

    INSERT INTO report_values (report_id, test_name, result, unit, reference_range_text, status)
    VALUES
      (v_report_id, 'Hemoglobin', '11.8', 'g/dL', '13.0 - 17.0', 'abnormal'),
      (v_report_id, 'Fasting Blood Sugar', '138', 'mg/dL', '70 - 100', 'abnormal'),
      (v_report_id, 'HbA1c', '7.8', '%', '< 5.7', 'abnormal'),
      (v_report_id, 'Total Cholesterol', '230', 'mg/dL', '< 200', 'abnormal'),
      (v_report_id, 'LDL Cholesterol', '160', 'mg/dL', '< 100', 'abnormal');

    INSERT INTO health_metrics (patient_id, metric_name, value, unit, recorded_date, source, report_id)
    VALUES
      (v_patient_id, 'Hemoglobin', 11.8, 'g/dL', NOW() - INTERVAL '120 days', 'report', v_report_id),
      (v_patient_id, 'Fasting Blood Sugar', 138, 'mg/dL', NOW() - INTERVAL '120 days', 'report', v_report_id),
      (v_patient_id, 'HbA1c', 7.8, '%', NOW() - INTERVAL '120 days', 'report', v_report_id),
      (v_patient_id, 'Total Cholesterol', 230, 'mg/dL', NOW() - INTERVAL '120 days', 'report', v_report_id),
      (v_patient_id, 'LDL Cholesterol', 160, 'mg/dL', NOW() - INTERVAL '120 days', 'report', v_report_id);

    -- Medication Schedules
    INSERT INTO medication_schedules (patient_id, medicine_name, strength, frequency, times, start_date, end_date, instructions, before_after_food, is_active)
    VALUES
      (v_patient_id, 'Glycomet 500', '500mg', 'twice_daily', '["08:00","20:00"]', CURRENT_DATE - 30, CURRENT_DATE + 60, 'Monitor blood sugar', 'after food', TRUE),
      (v_patient_id, 'Atorvastatin 10mg', '10mg', 'once_daily_night', '["21:00"]', CURRENT_DATE - 30, CURRENT_DATE + 60, 'At night', 'after food', TRUE),
      (v_patient_id, 'Aspirin 75mg', '75mg', 'once_daily_morning', '["07:00"]', CURRENT_DATE - 30, NULL, 'With water', 'after food', TRUE);

    -- Symptom
    INSERT INTO symptoms (patient_id, description, duration, severity, language)
    VALUES
      (v_patient_id, 'Mild headache and fatigue', '3 days', 'mild', 'en'),
      (v_patient_id, 'Increased thirst and frequent urination', '1 week', 'moderate', 'en');

    -- Emergency Contact
    INSERT INTO emergency_contacts (patient_id, name, relationship, phone, is_primary)
    VALUES (v_patient_id, 'Sujatha Kumar', 'Spouse', '9876500000', TRUE);

    -- Family Member
    INSERT INTO family_members (patient_id, name, relationship, date_of_birth, gender, blood_group)
    VALUES (v_patient_id, 'Kavitha Kumar', 'Spouse', '1992-03-10', 'Female', 'B+');

    -- Appointment
    INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason, status)
    SELECT v_patient_id, d.id, NOW() + INTERVAL '3 days', 'Follow-up for diabetes management', 'confirmed'
    FROM doctors d JOIN users u ON d.user_id = u.id WHERE u.email = 'doctor@medvision.ai';

    -- Notifications
    INSERT INTO notifications (user_id, title, message, notification_type, is_read)
    SELECT u.id, 'Report Analysis Complete',
      'Your blood report from City Diagnostics has been analyzed. 3 values need attention.',
      'report', FALSE
    FROM users u WHERE u.email = 'patient@medvision.ai';

    INSERT INTO notifications (user_id, title, message, notification_type, is_read)
    SELECT u.id, 'Medicine Reminder',
      'Time to take Glycomet 500mg (after food).',
      'reminder', FALSE
    FROM users u WHERE u.email = 'patient@medvision.ai';

  END IF;
END $$;
