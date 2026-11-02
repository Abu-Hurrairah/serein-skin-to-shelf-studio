@echo off
setlocal
cd /d "%~dp0"
set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not exist "%PY%" set "PY=python"
echo -----------------------------------------------
echo SEREIN - First-time setup
 echo -----------------------------------------------
"%PY%" -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo Setup failed. Confirm Python 3.12 is installed.
  pause
  exit /b 1
)
if not exist .env copy .env.example .env >nul
echo.
echo Setup complete. For live YouCam, run CONNECT_YOUCAM_WINDOWS.bat and paste your account key securely.
echo Then double-click START_WINDOWS.bat
pause
