@echo off
setlocal
cd /d "%~dp0"

echo ===================================================
echo   Aurora CSPM - Automated Setup and Start (Simple)
echo ===================================================
echo.

:: 1. Backend
echo [1/2] Configuring Backend...
if not exist "backend\data" mkdir "backend\data"
if exist "*.parquet" move "*.parquet" "backend\data\" >nul

cd backend
if not exist venv (
    echo   Creating venv...
    python -m venv venv
)
echo   Installing deps...
call venv\Scripts\activate
pip install -r requirements.txt >nul 2>&1

echo   Starting Backend...
start "Backend" cmd /k "call venv\Scripts\activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
cd ..

:: 2. Dashboard
echo.
echo [2/2] Configuring Dashboard...
cd dashboard
if not exist node_modules (
    echo   Installing npm modules...
    call npm install
)

echo   Starting Frontend...
start "Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ===================================================
echo   Running! Close this window whenever.
echo ===================================================
pause
