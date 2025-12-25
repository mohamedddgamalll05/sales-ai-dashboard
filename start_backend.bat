@echo off
echo ========================================
echo Starting FastAPI Backend Server
echo ========================================
echo.
echo Make sure MongoDB is running first!
echo.
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
pause

