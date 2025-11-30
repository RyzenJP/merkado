@echo off
echo ========================================
echo Starting ML Recommendation Service
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Checking Python installation...
python --version

echo.
echo [2/3] Installing dependencies (if needed)...
pip install -r requirements.txt --quiet

echo.
echo [3/3] Starting Flask service...
echo.
echo Service will be available at: http://localhost:5000
echo Press Ctrl+C to stop the service
echo.

python app.py

pause

