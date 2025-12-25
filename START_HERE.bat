@echo off
echo ========================================
echo Sales AI Dashboard - Quick Start
echo ========================================
echo.

cd /d "%~dp0"

echo Step 1: Checking MongoDB...
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://127.0.0.1:27017', serverSelectionTimeoutMS=2000); client.admin.command('ping'); print('✅ MongoDB is running')" 2>nul
if errorlevel 1 (
    echo ❌ MongoDB is not running!
    echo    Please start MongoDB first: mongod
    pause
    exit /b 1
)

echo.
echo Step 2: Checking dependencies...
python -c "import sklearn; print('✅ Dependencies OK')" 2>nul
if errorlevel 1 (
    echo.
    echo ❌ Dependencies not installed!
    echo    Please run: pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo Step 3: Initializing project (loading data and training model)...
python init_project.py
if errorlevel 1 (
    echo.
    echo ❌ Initialization failed!
    echo    Check the error messages above.
    echo.
    echo    If you see dependency errors, run:
    echo    pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo Step 4: Starting FastAPI backend...
echo    Backend will run on http://127.0.0.1:8000
echo    Press Ctrl+C to stop the backend
echo.
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

