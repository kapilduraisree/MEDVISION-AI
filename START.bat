@echo off
REM ============================================================
REM MedVision AI - Windows Quick Start
REM Run this once to set up the virtual environment and launch
REM ============================================================

echo.
echo  ==========================================
echo   MedVision AI - Streamlit Setup ^& Launch
echo  ==========================================
echo.

REM ?? Step 1: Create venv if it doesn't exist ??????????????
if not exist "venv\" (
    echo [1/5] Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Python not found. Install Python 3.11+ and try again.
        pause
        exit /b 1
    )
) else (
    echo [1/5] Virtual environment already exists.
)

REM ?? Step 2: Activate venv ????????????????????????????????
echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

REM ?? Step 3: Install dependencies ?????????????????????????
echo [3/5] Installing dependencies (this may take a few minutes)...
pip install -r requirements.txt --quiet

REM ?? Step 4: Create .env if missing ???????????????????????
if not exist ".env" (
    echo [4/5] Creating .env from template...
    copy .env.example .env
    echo.
    echo  ** ACTION REQUIRED: Edit .env and set DATABASE_URL **
    echo  ** Press any key after editing .env to continue...  **
    pause
) else (
    echo [4/5] .env file found.
)

REM ?? Step 5: Launch Streamlit ?????????????????????????????
echo [5/5] Starting MedVision AI...
echo.
echo  Open your browser at: http://localhost:8501
echo  Press Ctrl+C to stop the server.
echo.
streamlit run app.py --server.port 8501

pause
