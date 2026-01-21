@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo   Aurora CSPM - Automated Setup and Start (Windows)
echo ===================================================

:: 1. Backend Setup
echo.
echo [1/2] Setting up Backend...

:: Ensure data files are in the right place
if not exist backend\data ( mkdir backend\data )
if exist test_ml_ready.parquet ( move /Y test_ml_ready.parquet backend\data\ )
if exist train_ml_ready.parquet ( move /Y train_ml_ready.parquet backend\data\ )

cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
echo Installing backend dependencies...
pip install -r requirements.txt
echo Starting Backend API...
start "Aurora Backend API" cmd /k "venv\Scripts\activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
cd ..

:: 2. Dashboard Setup
echo.
echo [2/2] Setting up Dashboard...
cd dashboard
if not exist node_modules (
    echo Installing dashboard dependencies...
    npm install
)
echo Starting Dashboard UI...
start "Aurora Dashboard UI" cmd /k "npm run dev"
cd ..

echo.
echo ===================================================
echo   System is starting up!
echo   API: http://localhost:8000
echo   UI:  http://localhost:3000
echo ===================================================
pause
