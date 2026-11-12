@echo off
echo ========================================================
echo  One Patient, Many Records - Starting Dev Servers
echo ========================================================
echo.

start "Backend (FastAPI :8000)" cmd /k "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

cd frontend
start "Frontend (Vite :5173)" cmd /k "npm run dev"

echo Backend: http://localhost:8000 (API Docs: http://localhost:8000/docs)
echo Frontend: http://localhost:5173
echo.
