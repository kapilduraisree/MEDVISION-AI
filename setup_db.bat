@echo off
REM ============================================================
REM MedVision AI - Database Setup Script
REM Run AFTER PostgreSQL is installed and running
REM ============================================================

echo.
echo  ==========================================
echo   MedVision AI - Database Setup
echo  ==========================================
echo.
echo  This will create the database, run the schema,
echo  and load sample data with demo accounts.
echo.
echo  Prerequisites:
echo    - PostgreSQL installed and running
echo    - psql available on PATH
echo.

set /p PGUSER=Enter PostgreSQL superuser (default: postgres): 
if "%PGUSER%"=="" set PGUSER=postgres

echo.
echo [1/4] Creating database and user...
psql -U %PGUSER% -c "CREATE USER medvision WITH PASSWORD 'medvision_secret';" 2>nul
psql -U %PGUSER% -c "CREATE DATABASE medvision_ai OWNER medvision;" 2>nul
psql -U %PGUSER% -c "GRANT ALL PRIVILEGES ON DATABASE medvision_ai TO medvision;" 2>nul

echo [2/4] Running schema (creating all tables)...
psql -U medvision -d medvision_ai -f database\schema.sql
if errorlevel 1 (
    echo ERROR: Schema creation failed. Check PostgreSQL connection.
    pause
    exit /b 1
)

echo [3/4] Loading sample data and demo accounts...
psql -U medvision -d medvision_ai -f database\sample_data.sql

echo [4/4] Done!
echo.
echo  Demo accounts created:
echo    Patient: patient@medvision.ai  / Password@123
echo    Doctor:  doctor@medvision.ai   / Password@123
echo    Admin:   admin@medvision.ai    / Password@123
echo.
echo  Now run START.bat to launch the app.
echo.
pause
