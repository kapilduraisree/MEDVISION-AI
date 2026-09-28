@echo off
echo ============================================================
echo  MedVision AI - Frontend Setup and Start
echo ============================================================

cd /d "%~dp0frontend"

REM Install node modules if missing
if not exist "node_modules" (
    echo Installing npm packages (this may take a few minutes)...
    npm install
    if errorlevel 1 (
        echo ERROR: npm install failed.
        pause
        exit /b 1
    )
)

echo.
echo Starting React frontend on http://localhost:3000
echo Press Ctrl+C to stop.
echo.

npm start
