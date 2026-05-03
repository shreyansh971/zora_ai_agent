#!/bin/bash
# Quick start script for Zora (Mac/Linux)
# Run: chmod +x start.sh && ./start.sh

echo ""
echo "  ██╗   ██╗███████╗██████╗  █████╗ "
echo "  ██║   ██║██╔════╝██╔══██╗██╔══██╗"
echo "  ██║   ██║█████╗  ██████╔╝███████║"
echo "  ╚██╗ ██╔╝██╔══╝  ██╔══██╗██╔══██║"
echo "   ╚████╔╝ ███████╗██║  ██║██║  ██║"
echo "    ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝"
echo "  The Integrity Agent"
echo ""

# Check .env
if [ ! -f .env ]; then
  echo "⚠️  No .env file found. Copying from .env.example..."
  cp .env.example .env
  echo "⚠️  Please edit .env and add your OPENAI_API_KEY, then re-run this script."
  exit 1
fi

# Check venv
if [ ! -d venv ]; then
  echo "📦 Creating Python virtual environment..."
  python3 -m venv venv
fi

echo "🐍 Activating Python environment..."
source venv/bin/activate

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt -q

echo "📦 Installing frontend dependencies..."
cd frontend && npm install --silent && cd ..

echo ""
echo "🚀 Starting Zora..."
echo ""

# Start backend in background
python -m backend.main &
BACKEND_PID=$!
echo "✅ Backend running (PID $BACKEND_PID) → http://localhost:8000"

# Wait for backend to start
sleep 2

# Start frontend
cd frontend
echo "✅ Starting frontend → http://localhost:5173"
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "🌐 Open your browser: http://localhost:5173"
echo "📖 API docs:          http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services."

# Wait and cleanup
trap "echo ''; echo 'Stopping...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
