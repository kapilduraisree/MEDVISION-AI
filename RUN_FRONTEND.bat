@echo off
title MedVision AI - Frontend
color 0B
echo.
echo  =====================================================
echo   MedVision AI - Frontend (React)
echo   URL: http://localhost:3000
echo  =====================================================
echo.

cd /d "%~dp0frontend"

if not exist "node_modules\react" (
    echo Installing npm packages - please wait 3-5 minutes...
    echo.
    npm install --legacy-peer-deps
    if errorlevel 1 (
        echo npm install failed. Try running as Administrator.
        pause
        exit /b 1
    )
)

echo.
echo  Frontend starting - browser will open automatically...
echo  Press Ctrl+C to stop
echo.

set BROWSER=none
set PORT=3000
set REACT_APP_API_URL=http://localhost:8000
npm start
pause
