@echo off
setlocal
cd /d "%~dp0"
set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not exist "%PY%" set "PY=python"
echo.
echo ---------------------------------------------
echo SEREIN - Verified YouCam screenshot capture
echo ---------------------------------------------
echo Real API result required. No sample images will be used.
echo Start START_WINDOWS.bat and configure your key first.
echo.
set /p "PHOTO=Enter full path to your own JPG/PNG portrait: "
if not defined PHOTO (echo No photo supplied. & pause & exit /b 1)
"%PY%" -m pip show playwright >nul 2>&1
if errorlevel 1 (
 echo Installing Playwright automation library...
 "%PY%" -m pip install playwright
 if errorlevel 1 (echo Install failed. & pause & exit /b 1)
)
"%PY%" tools\capture_verified_live.py "%PHOTO%"
echo.
pause
