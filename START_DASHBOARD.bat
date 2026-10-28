@echo off
title Cotton Farm Intelligence Dashboard
echo.
echo ====================================================
echo   Cotton Farm Intelligence - Dhule, Maharashtra
echo   Starting Backend and Frontend...
echo ====================================================
echo.

echo [1/2] Starting FastAPI Backend on port 8000...
start "Backend API" cmd /k "cd /d %~dp0cotton_farm_intelligence\backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 4 /nobreak > nul

echo [2/2] Starting Vite Frontend on port 5173...
start "Frontend Dashboard" cmd /k "cd /d %~dp0cotton_farm_intelligence\frontend && npm run dev"

timeout /t 5 /nobreak > nul

echo.
echo ====================================================
echo   Dashboard is RUNNING!
echo   Frontend : http://localhost:5173
echo   Backend  : http://localhost:8000
echo   API Docs : http://localhost:8000/docs
echo ====================================================
echo.
start http://localhost:5173
echo Press any key to close this launcher...
pause > nul