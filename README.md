# MedVision AI — Streamlit Medical AI Platform

> **Final Year College Project** · Full-Stack Healthcare Platform  
> ⚠️ *For educational and informational use only. Not a substitute for professional medical advice.*

---

## What Changed (v2.0)

The original React + FastAPI stack has been replaced with a single **Streamlit** application.  
Everything runs from one command — no separate frontend/backend servers.

| Before (v1) | After (v2) |
|-------------|------------|
| React 18 + Vite frontend | Streamlit single-file app |
| FastAPI backend (REST API) | Direct PostgreSQL via SQLAlchemy |
| JWT auth via HTTP | Session-state auth in Streamlit |
| npm + uvicorn (2 processes) | `streamlit run app.py` (1 process) |

---

## Features

| Feature | Description |
|---------|-------------|
| 🔬 OCR Report Analysis | Upload blood/scan reports — AI extracts and explains every value |
| 📋 Prescription Analyzer | Photo-to-text extraction of medicines |
| 💊 Medicine Strip Scanner | Scan packaging for expiry, batch no, MRP |
| ⚗️ Drug Interaction Checker | Verify safety of multiple medicines together |
| 🤖 AI Chatbot | Tamil & English bilingual medical Q&A |
| ⏰ Medicine Reminders | Schedule and track medication adherence |
| 📈 Health Trend Charts | Visual tracking of lab values over time |
| 🧠 AI Health Summary | Multimodal summary from symptoms + reports + meds |
| 👨‍👩‍👧 Family Profiles | Manage records for entire family |
| 🔒 Medical Locker | Secure document storage |
| 🩺 Doctor Dashboard | Patient review, notes, appointment management |
| 🛡️ Admin Dashboard | Analytics, user/doctor/medicine management |

---

## Quick Start (Windows)

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Tesseract OCR *(optional — mock data used if not installed)*

### 1. Set up the database
```
SETUP_DB.bat
```

### 2. Start the app
```
START.bat
```
Opens at **http://localhost:8501**

---

## Manual Setup

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env — set DATABASE_URL at minimum

# Set up database (after PostgreSQL is running)
psql -U medvision -d medvision_ai -f database/schema.sql
psql -U medvision -d medvision_ai -f database/sample_data.sql

# Launch
streamlit run app.py
```

---

## Project Structure

```
MEDVISION-AI/
├── app.py                      # Main entry point — router + sidebar
├── requirements.txt
├── .env.example                # Environment variable template
├── .streamlit/
│   └── config.toml             # Dark theme + server config
├── app/
│   ├── core/
│   │   ├── config.py           # Settings (env vars)
│   │   ├── database.py         # SQLAlchemy engine + helpers
│   │   ├── auth.py             # Login, register, session state
│   │   └── utils.py            # Shared UI helpers
│   ├── services/ai/
│   │   ├── ocr_service.py      # Tesseract OCR + mock fallback
│   │   ├── report_explainer.py # Lab value explanations (EN/TA)
│   │   ├── chatbot_service.py  # Medical chatbot (OpenAI + rule-based)
│   │   ├── drug_interactions.py# Pairwise drug interaction checker
│   │   ├── health_summary.py   # Multimodal AI health summary
│   │   ├── medicine_scanner.py # Strip scan + expiry checker
│   │   └── prescription_analyzer.py # Rx image extraction
│   └── pages/
│       ├── login.py / register.py
│       ├── patient/            # 16 patient pages
│       ├── doctor/             # 3 doctor pages
│       └── admin/              # 5 admin pages
├── database/
│   ├── schema.sql              # Full PostgreSQL schema
│   └── sample_data.sql         # Demo data + accounts
└── uploads/                    # Uploaded files (auto-created)
```

---

## Environment Variables

```env
# Required
DATABASE_URL=postgresql://medvision:medvision_secret@localhost:5432/medvision_ai
SECRET_KEY=your-secret-key-minimum-32-characters

# Optional AI APIs
OPENAI_API_KEY=sk-...           # Enables GPT chatbot + summaries
```

---

## Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Patient | patient@medvision.ai | Password@123 |
| Doctor | doctor@medvision.ai | Password@123 |
| Admin | admin@medvision.ai | Password@123 |

---

## AI Safety

- ✅ Never diagnoses diseases or medical conditions  
- ✅ Never prescribes medications or recommends dosage changes  
- ✅ All AI outputs clearly labelled as informational  
- ✅ Emergency symptoms trigger 112 alert immediately  
- ✅ Professional consultation always recommended  
- ✅ Bilingual (English + Tamil) disclaimers on every AI response  

---

## Optional: Tesseract OCR

For live OCR instead of mock data:

**Windows:**
1. Download installer from https://github.com/UB-Mannheim/tesseract/wiki
2. Install and note the path (e.g. `C:\Program Files\Tesseract-OCR\tesseract.exe`)
3. Add to system PATH or set in `.env`:
   ```
   TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata
   ```

For Tamil language support, install the `tam` language pack during Tesseract installation.

---

*Built as a college final year project. All medical information is for educational purposes only.*
