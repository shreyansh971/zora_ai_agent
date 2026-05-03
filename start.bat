@echo off
echo.
echo   ZORA - The Integrity Agent
echo   Multi-Agent Research System
echo.

REM Check .env
IF NOT EXIST .env (
    echo [WARNING] No .env file found. Copying from .env.example...
    copy .env.example .env
    echo [ACTION REQUIRED] Open .env and add your OPENAI_API_KEY, then re-run this script.
    pause
    exit /b 1
)

REM Create venv if not exists
IF NOT EXIST venv (
    echo [SETUP] Creating Python virtual environment...
    python -m venv venv
)

echo [SETUP] Activating virtual environment...
call venv\Scripts\activate.bat

echo [SETUP] Installing Python dependencies (first run takes 3-5 min)...
pip install -r requirements.txt -q

echo [SETUP] Installing frontend dependencies...
cd frontend
call npm install --silent
cd ..

echo.
echo [START] Launching Zora backend...
start "Zora Backend" cmd /k "call venv\Scripts\activate.bat && python -m backend.main"

echo [START] Waiting for backend to initialize...
timeout /t 3 /nobreak > nul

echo [START] Launching Zora frontend...
start "Zora Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo =============================================
echo  Zora is starting up!
echo  Open your browser: http://localhost:5173
echo  API docs:          http://localhost:8000/docs
echo =============================================
echo.
pause
