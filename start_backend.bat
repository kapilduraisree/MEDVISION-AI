@echo off
echo ============================================================
echo  MedVision AI - Backend Setup and Start
echo ============================================================

cd /d "%~dp0backend"

REM Create virtual environment if it doesn't exist
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create venv. Make sure Python 3.11+ is installed.
        pause
        exit /b 1
    )
    echo Virtual environment created.
)

REM Activate venv
call venv\Scripts\activate.bat

REM Upgrade pip silently
python -m pip install --upgrade pip -q

REM Install dependencies
echo Installing Python dependencies (first run takes ~2 minutes)...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ERROR: pip install failed. See above for details.
    pause
    exit /b 1
)

REM Copy .env from project root if not present in backend/
if not exist ".env" (
    if exist "..\.env" (
        copy "..\.env" ".env" >nul
        echo Copied .env from project root.
    )
)

REM Create upload directories
for %%d in (uploads uploads\reports uploads\prescriptions uploads\medicines uploads\bills uploads\documents uploads\profiles uploads\tts uploads\voice) do (
    if not exist "%%d" mkdir "%%d"
)

REM Seed demo data (safe to run multiple times - skips existing records)
echo.
echo Seeding demo data...
python seed_data.py

echo.
echo ============================================================
echo  Backend running at  http://localhost:8000
echo  API Docs at         http://localhost:8000/api/docs
echo  Press Ctrl+C to stop
echo ============================================================
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
