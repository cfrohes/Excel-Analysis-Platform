#!/bin/bash

# Excel Data Analysis Platform - Startup Script

echo "🚀 Starting Excel Data Analysis Platform..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use. Please stop the service using this port."
        return 1
    else
        return 0
    fi
}

# Check if ports are available
echo "🔍 Checking if ports are available..."
if ! check_port 8000; then
    exit 1
fi
if ! check_port 3000; then
    exit 1
fi

# Setup backend
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "📥 Installing backend dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating environment configuration..."
    cp env.example .env
    echo "📝 Please edit backend/.env file and add your OpenAI API key:"
    echo "   OPENAI_API_KEY=your_openai_api_key_here"
    echo ""
    read -p "Press Enter after you've configured the .env file..."
fi

# Create uploads directory
mkdir -p uploads

# Start backend in background
echo "🚀 Starting backend server..."
python run.py &
BACKEND_PID=$!

# Go back to root directory
cd ..

# Setup frontend
echo "🔧 Setting up frontend..."
cd frontend

# Install frontend dependencies
echo "📥 Installing frontend dependencies..."
npm install

# Start frontend
echo "🚀 Starting frontend server..."
npm start &
FRONTEND_PID=$!

# Wait a moment for servers to start
sleep 5

echo ""
echo "✅ Excel Data Analysis Platform is starting up!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "📁 To stop the servers, press Ctrl+C"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped."
    exit 0
}

# Set up trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop the servers
wait
