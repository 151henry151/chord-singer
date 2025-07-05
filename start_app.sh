#!/bin/bash

# Chord-Singer Application Startup Script
# This script starts both the backend (FastAPI) and frontend (React) servers

set -e  # Exit on any error

echo "🎵 Starting Chord-Singer Application..."
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "backend/main.py" ] || [ ! -f "frontend/package.json" ]; then
    print_error "Please run this script from the chord-singer root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Creating one..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Check if backend dependencies are installed
if ! python -c "import fastapi, uvicorn" 2>/dev/null; then
    print_status "Installing backend dependencies..."
    pip install -r requirements.txt
    print_success "Backend dependencies installed"
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    print_status "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    print_success "Frontend dependencies installed"
fi

# Function to cleanup background processes on exit
cleanup() {
    print_status "Shutting down servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    print_success "Servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend server
print_status "Starting backend server (FastAPI) on http://localhost:8000..."
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend is running
if ! curl -s http://localhost:8000/health >/dev/null 2>&1; then
    print_warning "Backend may not be fully started yet, continuing..."
else
    print_success "Backend server is running"
fi

# Start frontend server
print_status "Starting frontend server (React) on http://localhost:3000..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 5

print_success "🎵 Chord-Singer is starting up!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for user to stop the servers
wait 