@echo off
title MedVision AI - Backend
color 0A
echo.
echo  =====================================================
echo   MedVision AI - Backend Server
echo   API: http://localhost:8000
echo   Docs: http://localhost:8000/api/docs
echo  =====================================================
echo.

cd /d "%~dp0backend"

if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

if not exist "venv\Lib\site-packages\fastapi" (
    echo Installing dependencies...
    pip install -r requirements.txt -q
)

echo Seeding demo data...
python seed_data.py

echo.
echo  Backend starting on http://localhost:8000
echo  Press Ctrl+C to stop
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
