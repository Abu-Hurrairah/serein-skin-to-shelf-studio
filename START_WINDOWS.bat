@echo off
setlocal
cd /d "%~dp0"
set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not exist "%PY%" set "PY=python"
if not exist .env copy .env.example .env >nul
 echo -----------------------------------------------
 echo SEREIN Professional v1.4 - http://127.0.0.1:8011
 echo -----------------------------------------------
echo New edition runs on 8011 to avoid a previous Serein server on port 8000.
start "" powershell -NoProfile -Command "Start-Sleep -Seconds 2; Start-Process http://127.0.0.1:8011"
"%PY%" -m uvicorn app.main:app --host 127.0.0.1 --port 8011
if errorlevel 1 (
 echo.
 echo If uvicorn is missing, run SETUP_WINDOWS.bat first.
 pause
)
