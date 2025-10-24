@echo off
echo Starting POS System...
echo.
echo The POS System will open in your default web browser.
echo Default login credentials:
echo Username: admin
echo Password: admin123
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0"
POS_System.exe
pause
