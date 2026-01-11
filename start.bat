@echo off
REM TimeTable Application Startup Script
REM Double-click this file to start the application

echo ================================================
echo    TimeTable - Flexible Task Management
echo ================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [2/3] Checking database...
if not exist "instance\timetable.db" (
    echo Database not found. Initializing...
    python init_db.py
    if errorlevel 1 (
        echo ERROR: Failed to initialize database
        pause
        exit /b 1
    )
)

echo [3/3] Starting application...
echo.
echo ================================================
echo   Application starting at http://localhost:5000
echo   Press CTRL+C to stop the server
echo ================================================
echo.

python run.py

pause
