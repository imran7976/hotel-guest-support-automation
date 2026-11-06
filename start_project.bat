@echo off
title Grand Azure Hotel AI Support Automation Launcher
color 0b

echo ==============================================================================
echo    GRAND AZURE RESORT & HOTEL - AI GUEST SUPPORT AUTOMATION SYSTEM
echo ==============================================================================
echo.
echo [1/3] Checking Environment and Database...
if not exist ".env" (
    echo Creating .env from .env.example...
    copy .env.example .env >nul
)

echo [2/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "Hotel Backend (FastAPI)" cmd /k "cd /d %~dp0backend && .\venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [3/3] Starting Next.js Frontend on http://localhost:3000 ...
start "Hotel Frontend (Next.js)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Waiting 5 seconds for servers to initialize...
timeout /t 5 /nobreak >nul

echo Opening Hotel Support Portal in your default browser...
start http://localhost:3000

echo.
echo ==============================================================================
echo    SUCCESS! Both servers are running in separate terminal windows.
echo    - Frontend Dashboard: http://localhost:3000
echo    - Backend API Docs:   http://127.0.0.1:8000/docs
echo.
echo    Do NOT close the black terminal windows while using the platform!
echo ==============================================================================
pause

