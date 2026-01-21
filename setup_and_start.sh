#!/bin/bash

echo "==================================================="
echo "  Aurora CSPM - Automated Setup and Start (Linux)"
echo "==================================================="

# 1. Backend Setup
echo ""
echo "[1/2] Setting up Backend..."

# Ensure data files are in the right place
mkdir -p backend/data
[ -f "test_ml_ready.parquet" ] && mv test_ml_ready.parquet backend/data/
[ -f "train_ml_ready.parquet" ] && mv train_ml_ready.parquet backend/data/

cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "Installing backend dependencies..."
pip install -r requirements.txt
echo "Starting Backend API in background..."
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
cd ..

# 2. Dashboard Setup
echo ""
echo "[2/2] Setting up Dashboard..."
cd dashboard
if [ ! -d "node_modules" ]; then
    echo "Installing dashboard dependencies..."
    npm install
fi
echo "Starting Dashboard UI in background..."
nohup npm run dev > ../dashboard.log 2>&1 &
cd ..

echo ""
echo "==================================================="
echo "  System is starting up!"
echo "  API: http://localhost:8000"
echo "  UI:  http://localhost:3000"
echo "  Logs: backend.log, dashboard.log"
echo "==================================================="
echo "Use 'killall node' and 'pkill uvicorn' to stop."
