#!/bin/bash
# Local development helper — not used in production
# AI Incident Responder - Startup Script

echo "🚀 Starting AI Incident Responder..."
echo ""

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating Python virtual environment..."
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "✅ Dependencies installed!"
echo ""
echo "Starting services..."
echo ""

# Start backend in background
echo "🔧 Starting backend on http://localhost:8000"
cd backend
source venv/bin/activate
python -m uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend on http://localhost:3000"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✨ Services started!"
echo ""
echo "📊 Backend: http://localhost:8000"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait


