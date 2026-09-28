# MedVision AI — Multimodal AI-Based Medicine & Health Report Analysis System

> **Final Year College Project** · Full-Stack Healthcare Platform  
> ⚠️ *For educational and informational use only. Not a substitute for professional medical advice.*

---

## Project Overview

MedVision AI is a complete, production-ready full-stack healthcare platform that combines:

- **OCR Medical Report Analysis** — Upload blood reports, scan reports; AI extracts and explains every value
- **Prescription Analyzer** — Photo-to-text prescription extraction with verification workflow
- **Medicine Strip Scanner** — Scan medicine packaging for expiry and drug information
- **Drug Interaction Checker** — Verify safety of multiple medicines taken together
- **AI Health Chatbot** — Tamil & English bilingual medical Q&A assistant
- **Smart Medicine Reminders** — Schedule and track medication adherence
- **Health Trend Charts** — Visual tracking of lab values over time
- **AI Health Summary** — Multimodal summary combining symptoms, reports, and medications
- **Family Health Profiles** — Manage health records for entire family
- **Medical Locker** — Secure document storage for all medical files
- **Doctor Dashboard** — Review patient data, add clinical notes, manage appointments
- **Admin Dashboard** — Full system management with analytics and audit logs

---

## Demo Accounts

| Role    | Email                      | Password      |
|---------|----------------------------|---------------|
| Patient | patient@medvision.ai       | Password@123  |
| Doctor  | doctor@medvision.ai        | Password@123  |
| Admin   | admin@medvision.ai         | Password@123  |

---

## Tech Stack

| Layer      | Technology                                      |
|------------|-------------------------------------------------|
| Frontend   | React 18, Tailwind CSS, Recharts, React Router  |
| Backend    | Python 3.11, FastAPI, SQLAlchemy                |
| Database   | PostgreSQL 15                                   |
| AI / OCR   | Tesseract OCR, OpenAI GPT (optional), gTTS      |
| Auth       | JWT (python-jose + passlib bcrypt)              |
| Charts     | Recharts                                        |
| Container  | Docker + Docker Compose                         |

---

## Project Structure

```
medvision ai/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── main.py             # App entry point
│   │   ├── core/               # Config, DB, Security
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── api/routes/         # All API route handlers
│   │   └── services/ai/        # OCR, chatbot, summariser
│   └── requirements.txt
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── App.jsx             # Router + auth guard
│   │   ├── pages/              # All 25+ pages
│   │   │   ├── patient/        # Patient-facing pages
│   │   │   ├── doctor/         # Doctor dashboard
│   │   │   └── admin/          # Admin dashboard
│   │   ├── components/         # Reusable UI components
│   │   ├── services/api.js     # Axios API service layer
│   │   ├── context/            # Auth context
│   │   └── i18n/               # Tamil + English translations
│   └── package.json
├── database/
│   ├── schema.sql              # Full PostgreSQL schema
│   └── sample_data.sql         # Demo data + users
├── .env.example                # Environment variable template
└── docker-compose.yml          # One-command startup
```

---

## Quick Start

### Option A — Docker (Recommended)

```bash
# 1. Clone / copy the project
cd "medvision ai"

# 2. Copy env file
cp .env.example .env

# 3. Start all services
docker-compose up --build

# 4. Open browser
# Frontend: http://localhost:3000
# API Docs:  http://localhost:8000/api/docs
```

### Option B — Manual Setup

#### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15
- Tesseract OCR (for live OCR)

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env
# Edit .env with your DATABASE_URL

# Run database migrations / create tables
# Tables are auto-created on first run

# Load sample data (after first run)
psql -U medvision -d medvision_ai -f ../database/sample_data.sql

# Start backend
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
# Opens at http://localhost:3000
```

#### PostgreSQL Setup

```bash
# Create database
createdb -U postgres medvision_ai
createuser -U postgres medvision

# Run schema
psql -U medvision -d medvision_ai -f database/schema.sql
psql -U medvision -d medvision_ai -f database/sample_data.sql
```

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Required
DATABASE_URL=postgresql://medvision:medvision_secret@localhost:5432/medvision_ai
SECRET_KEY=your-super-secret-key-minimum-32-characters

# Optional – AI APIs (system uses mock data if not set)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
```

---

## API Documentation

Interactive Swagger UI available at: `http://localhost:8000/api/docs`  
ReDoc available at: `http://localhost:8000/api/redoc`

### Key Endpoints

| Method | Endpoint                          | Description                    |
|--------|-----------------------------------|--------------------------------|
| POST   | `/api/v1/auth/register`           | Create new account             |
| POST   | `/api/v1/auth/login`              | Login, receive JWT             |
| GET    | `/api/v1/patients/profile`        | Get patient profile            |
| GET    | `/api/v1/patients/dashboard-summary` | Patient dashboard data      |
| POST   | `/api/v1/reports/upload`          | Upload & OCR analyze report    |
| GET    | `/api/v1/reports/{id}`            | Get report with explanations   |
| POST   | `/api/v1/prescriptions/upload`    | Analyze prescription image     |
| POST   | `/api/v1/medicines/scan-strip`    | Scan medicine packaging        |
| GET    | `/api/v1/medicines/search`        | Search medicine database       |
| POST   | `/api/v1/drug-interactions/check` | Check drug interactions        |
| POST   | `/api/v1/reminders/`              | Create medicine reminder       |
| POST   | `/api/v1/chatbot/message`         | Send message to AI chatbot     |
| POST   | `/api/v1/ai-summary/generate`     | Generate health summary        |
| GET    | `/api/v1/health-metrics/trends`   | Get health trend data          |
| POST   | `/api/v1/pharmacy-bills/upload`   | Scan pharmacy bill             |
| GET    | `/api/v1/admin/analytics`         | System analytics (admin only)  |

---

## Pages Index

| Page                  | Route                | Access   |
|-----------------------|----------------------|----------|
| Landing Page          | `/`                  | Public   |
| Login                 | `/login`             | Public   |
| Register              | `/register`          | Public   |
| Patient Dashboard     | `/dashboard`         | Patient  |
| Patient Profile       | `/profile`           | Patient  |
| Symptom Tracker       | `/symptoms`          | Patient  |
| Voice Input           | `/voice-input`       | Patient  |
| Upload Report         | `/reports`           | Patient  |
| Explain My Report     | `/reports/:id`       | Patient/Doctor |
| Prescription Analyzer | `/prescriptions`     | Patient  |
| Medicine Info         | `/medicines`         | All      |
| Medicine Scanner      | `/medicine-scan`     | Patient  |
| Drug Interactions     | `/drug-interactions` | Patient/Doctor |
| Reminders             | `/reminders`         | Patient  |
| Pharmacy Bills        | `/pharmacy-bills`    | Patient  |
| Health Trends         | `/health-trends`     | Patient  |
| AI Summary            | `/ai-summary`        | Patient  |
| AI Chatbot            | `/chatbot`           | All      |
| Medical Locker        | `/locker`            | Patient  |
| Family Profiles       | `/family`            | Patient  |
| Appointments          | `/appointments`      | Patient  |
| Emergency             | `/emergency`         | Patient  |
| Notifications         | `/notifications`     | All      |
| Settings              | `/settings`          | All      |
| Doctor Dashboard      | `/doctor/dashboard`  | Doctor   |
| Doctor Patients       | `/doctor/patients`   | Doctor   |
| Doctor Appointments   | `/doctor/appointments` | Doctor |
| Admin Dashboard       | `/admin/dashboard`   | Admin    |
| Admin Users           | `/admin/users`       | Admin    |
| Admin Doctors         | `/admin/doctors`     | Admin    |
| Admin Medicines       | `/admin/medicines`   | Admin    |
| Audit Logs            | `/admin/audit-logs`  | Admin    |

---

## AI Safety Compliance

This system adheres to all medical AI safety requirements:

- ✅ Never diagnoses diseases or medical conditions
- ✅ Never prescribes medications or recommends dosage changes  
- ✅ Never tells patients to stop prescribed medications
- ✅ All AI content clearly labelled as informational
- ✅ Low-confidence OCR results explicitly flagged
- ✅ Emergency symptoms trigger urgent-care alert (not diagnosis)
- ✅ Professional consultation always recommended
- ✅ Audit trail maintained for all AI-generated summaries
- ✅ Verified medicine database distinguishes from AI explanations

---

## Demo Flow (for Viva)

1. Register as patient → fill profile
2. Enter symptoms via text or voice input
3. Upload a blood report → view OCR extraction
4. Read AI explanation of each test value in Tamil/English
5. Upload a prescription → view extracted medicines
6. Scan a medicine strip → view expiry/batch info
7. Run drug interaction check on multiple medicines
8. Set medicine reminder with schedule
9. Upload pharmacy bill → view expense analysis
10. View health trends chart over 6 months
11. Generate AI health summary
12. Chat with AI assistant in Tamil
13. Log in as doctor → view patient data, add note
14. Log in as admin → view system analytics

---

## Known Limitations

- OCR accuracy depends on image quality; mock data is used when Tesseract is not installed
- AI chatbot uses rule-based fallback if OpenAI API key is not configured  
- Speech recognition uses browser Web Speech API (Chrome recommended)
- Text-to-speech uses browser SpeechSynthesis API
- TTS for Tamil may vary across operating systems and browsers

---

## License

MIT License — Free for educational use.

---

*Built with ❤️ as a college final year project. All medical information in this system is for educational purposes only.*
