@echo off
echo ============================================================
echo  MedVision AI - Database Setup
echo ============================================================
echo.
echo This script sets up the PostgreSQL database.
echo Make sure PostgreSQL is installed and running.
echo.

REM Default connection values - change these to match your setup
set PGHOST=localhost
set PGPORT=5432
set PGUSER=postgres

echo Step 1: Creating database user 'medvision'...
psql -U %PGUSER% -h %PGHOST% -p %PGPORT% -c "CREATE USER medvision WITH PASSWORD 'medvision_secret';" 2>nul
echo (If 'already exists' error appeared, that is fine.)

echo.
echo Step 2: Creating database 'medvision_ai'...
psql -U %PGUSER% -h %PGHOST% -p %PGPORT% -c "CREATE DATABASE medvision_ai OWNER medvision;" 2>nul
psql -U %PGUSER% -h %PGHOST% -p %PGPORT% -c "GRANT ALL PRIVILEGES ON DATABASE medvision_ai TO medvision;" 2>nul

echo.
echo Step 3: Running schema...
psql -U medvision -h %PGHOST% -p %PGPORT% -d medvision_ai -f database\schema.sql
if errorlevel 1 (
    echo ERROR: Schema creation failed. Check your PostgreSQL connection.
    pause
    exit /b 1
)

echo.
echo Step 4: Loading sample data...
psql -U medvision -h %PGHOST% -p %PGPORT% -d medvision_ai -f database\sample_data.sql
if errorlevel 1 (
    echo WARNING: Sample data load had errors - some data may already exist.
)

echo.
echo ============================================================
echo  Database setup complete!
echo  Connection: postgresql://medvision:medvision_secret@localhost:5432/medvision_ai
echo ============================================================
pause
