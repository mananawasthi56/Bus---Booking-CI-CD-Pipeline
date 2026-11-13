
@echo off
title BusGo - Full Stack Application

echo ==================================
echo       BUSGO APPLICATION
echo ==================================

echo Starting Backend...
start "BusGo Backend" cmd /k "cd /d %~dp0 && venv\Scripts\activate && uvicorn app.main:app --reload"

timeout /t 3 /nobreak >nul

echo Starting Frontend...
start "BusGo Frontend" cmd /k "cd /d %~dp0frontend && python -m http.server 5500"

timeout /t 2 /nobreak >nul

echo Opening BusGo in browser...
start http://127.0.0.1:5500/index.html

echo.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://127.0.0.1:5500
echo API Docs: http://127.0.0.1:8000/docs
echo.
pause
