# ⚡ Quick Start Guide

## Current Status

✅ **Python installed**: Python 3.12.4  
✅ **Dependencies installed**: All packages available  
✅ **Flask app**: Ready to run  
⚠️ **Database**: Needs configuration

## To Start the Service

### Option 1: Use Batch File (Easiest)
```bash
start.bat
```

### Option 2: Use PowerShell Script
```powershell
.\start.ps1
```

### Option 3: Manual Start
```bash
python app.py
```

## Database Configuration

The service needs database access. You have 3 options:

### Option A: Use Local XAMPP Database

1. Make sure XAMPP MySQL is running
2. Create/import your database locally
3. Update `app.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'your_local_database_name',
    'user': 'root',
    'password': ''  # XAMPP default
}
```

### Option B: Use Remote/Production Database

Update `app.py` with correct credentials:
```python
DB_CONFIG = {
    'host': 'your_host',
    'database': 'your_database',
    'user': 'your_username',
    'password': 'your_password'
}
```

### Option C: Use Environment Variables

Set environment variables:
```powershell
$env:DB_HOST = "localhost"
$env:DB_NAME = "your_database"
$env:DB_USER = "your_username"
$env:DB_PASSWORD = "your_password"
```

## After Starting

1. **Service will be available at**: http://localhost:5000

2. **Train models** (first time):
```powershell
Invoke-WebRequest -Uri http://localhost:5000/train -Method POST
```

3. **Test health**:
```powershell
Invoke-WebRequest -Uri http://localhost:5000/health
```

4. **Get recommendations**:
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/recommendations/1?limit=10"
```

## Note

The service will start even if database connection fails initially. It will attempt to connect when:
- Training models (`/train` endpoint)
- Getting recommendations (`/recommendations/<id>` endpoint)

If database connection fails, you'll see helpful error messages.

