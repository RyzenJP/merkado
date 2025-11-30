# PowerShell script to start ML Recommendation Service

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting ML Recommendation Service" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[1/3] Checking Python installation..." -ForegroundColor Green
    Write-Host $pythonVersion
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[2/3] Installing dependencies (if needed)..." -ForegroundColor Green
pip install -r requirements.txt --quiet

Write-Host ""
Write-Host "[3/3] Starting Flask service..." -ForegroundColor Green
Write-Host ""
Write-Host "Service will be available at: http://localhost:5000" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the service" -ForegroundColor Yellow
Write-Host ""

# Start the service
python app.py

