@echo off
echo 🚀 Starting AINZUNI Chatbot with Llama 3.1:8b...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Start the server
echo 🌐 Starting Flask server...
echo.
echo ✅ Server will be available at: http://localhost:5000
echo 📡 Press Ctrl+C to stop the server
echo.
python llama_server.py

pause
