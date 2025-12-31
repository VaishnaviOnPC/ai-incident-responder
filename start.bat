REM Local development helper — not used in production

@echo off
REM AI Incident Responder - Startup Script for Windows

echo 🚀 Starting AI Incident Responder...
echo.

REM Check if virtual environment exists
if not exist "backend\venv" (
    echo 📦 Creating Python virtual environment...
    cd backend
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    cd ..
)

REM Check if node_modules exists
if not exist "frontend\node_modules" (
    echo 📦 Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

echo.
echo ✅ Dependencies installed!
echo.
echo Starting services...
echo.

REM Start backend
echo 🔧 Starting backend on http://localhost:8000
start "Backend" cmd /k "cd backend && venv\Scripts\activate && python -m uvicorn main:app --reload --port 8000"

REM Wait a bit
timeout /t 3 /nobreak >nul

REM Start frontend
echo 🎨 Starting frontend on http://localhost:3000
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ✨ Services started!
echo.
echo 📊 Backend: http://localhost:8000
echo 🎨 Frontend: http://localhost:3000
echo.
echo Close the command windows to stop the services.

pause


