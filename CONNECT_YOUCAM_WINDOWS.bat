@echo off
setlocal
cd /d "%~dp0"
echo SEREIN - Secure YouCam API configuration
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0CONNECT_YOUCAM_WINDOWS.ps1"
if errorlevel 1 (echo Configuration not saved. & pause & exit /b 1)
echo Restart START_WINDOWS.bat and run a consented scan to verify the API.
pause
