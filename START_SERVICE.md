# 🚀 How to Start the ML Recommendation Service

## Quick Start

### Step 1: Install Dependencies

```bash
cd ml_service
pip install -r requirements.txt
```

### Step 2: Configure Database

Edit `app.py` and update `DB_CONFIG` with your database credentials:

**For Local XAMPP:**
```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'your_database_name',
    'user': 'root',
    'password': ''  # XAMPP default is empty
}
```

**For Production:**
```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'u520834156_dbBagoMerkado',
    'user': 'u520834156_userBMerkado25',
    'password': 's;h7TLSLl?4'
}
```

### Step 3: Start the Service

```bash
python app.py
```

You should see:
```
Loading recommendation models...
Starting Flask recommendation service on http://localhost:5000
 * Running on http://0.0.0.0:5000
```

### Step 4: Train Models (First Time)

In another terminal:
```bash
curl -X POST http://localhost:5000/train
```

Or use PowerShell:
```powershell
Invoke-WebRequest -Uri http://localhost:5000/train -Method POST
```

### Step 5: Test the Service

```bash
# Health check
curl http://localhost:5000/health

# Get recommendations for customer ID 123
curl "http://localhost:5000/recommendations/123?limit=10"
```

## Troubleshooting

### Issue: "Access denied for user"
- **Solution**: Check database credentials in `app.py`
- Make sure MySQL/XAMPP is running
- Verify database name, username, and password

### Issue: "Module not found"
- **Solution**: Install dependencies: `pip install -r requirements.txt`

### Issue: "Port 5000 already in use"
- **Solution**: Change port in `app.py`:
  ```python
  app.run(host='0.0.0.0', port=5001, debug=True)
  ```

### Issue: "No data available for training"
- **Solution**: Make sure you have:
  - Orders in the database
  - Products in the database
  - At least some user interaction data

## Running in Background (Windows)

### Option 1: PowerShell Background Job
```powershell
Start-Job -ScriptBlock { cd C:\xampp\htdocs\dti\ml_service; python app.py }
```

### Option 2: Windows Task Scheduler
Create a scheduled task to run `python app.py` on startup.

### Option 3: Use a Process Manager
Use tools like:
- PM2 (with pm2-windows-service)
- NSSM (Non-Sucking Service Manager)
- Windows Service Wrapper

## Integration with PHP

The PHP `RecommendationEngine` will automatically try the ML service first:

```php
// In config/RecommendationEngine.php
$ml_recs = $this->getMLRecommendations($customer_id, $limit);
if (!empty($ml_recs)) {
    return $ml_recs;  // Uses ML recommendations
}
// Falls back to PHP engine if ML unavailable
```

## Next Steps

1. ✅ Start the service: `python app.py`
2. ✅ Train models: `curl -X POST http://localhost:5000/train`
3. ✅ Test recommendations: `curl http://localhost:5000/recommendations/1`
4. ✅ The PHP app will automatically use ML service when available!

