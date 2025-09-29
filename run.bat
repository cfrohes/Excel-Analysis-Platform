@echo off
REM Excel Data Analysis Platform - Windows Startup Script

echo 🚀 Starting Excel Data Analysis Platform...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16 or higher.
    pause
    exit /b 1
)

REM Setup backend
echo 🔧 Setting up backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install backend dependencies
echo 📥 Installing backend dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo ⚙️  Creating environment configuration...
    copy env.example .env
    echo 📝 Please edit backend\.env file and add your OpenAI API key:
    echo    OPENAI_API_KEY=your_openai_api_key_here
    echo.
    pause
)

REM Create uploads directory
if not exist "uploads" mkdir uploads

REM Start backend in background
echo 🚀 Starting backend server...
start /b python run.py

REM Go back to root directory
cd ..

REM Setup frontend
echo 🔧 Setting up frontend...
cd frontend

REM Install frontend dependencies
echo 📥 Installing frontend dependencies...
npm install

REM Start frontend
echo 🚀 Starting frontend server...
start /b npm start

REM Wait a moment for servers to start
timeout /t 5 /nobreak >nul

echo.
echo ✅ Excel Data Analysis Platform is starting up!
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔌 Backend API: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo.
echo 📁 To stop the servers, close this window or press Ctrl+C
echo.

REM Keep the window open
pause
