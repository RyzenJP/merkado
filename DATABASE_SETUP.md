# 🔧 Database Setup for ML Service

## Current Issue

The ML service cannot connect to the database. You need to configure the correct database credentials.

## Solution Options

### Option 1: Use Local XAMPP Database (Recommended for Development)

1. **Make sure XAMPP MySQL is running**
   - Open XAMPP Control Panel
   - Start MySQL service

2. **Find your local database name**
   - Open phpMyAdmin (http://localhost/phpmyadmin)
   - Check what databases you have
   - Or check your PHP `config/database.php` for the database name

3. **Update `ml_service/app.py`**:

```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'your_local_database_name',  # ← Change this
    'user': 'root',                          # ← Usually 'root' for XAMPP
    'password': ''                           # ← Usually empty for XAMPP
}
```

**Example** (if your database is called `dti`):
```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'dti',
    'user': 'root',
    'password': ''
}
```

### Option 2: Use Remote/Production Database

If you want to use the production database, you need the correct credentials:

```python
DB_CONFIG = {
    'host': 'your_host',           # e.g., 'localhost' or remote IP
    'database': 'your_database',   # e.g., 'u520834156_dbBagoMerkado'
    'user': 'your_username',       # e.g., 'u520834156_userBMerkado25'
    'password': 'your_password'    # Your actual password
}
```

### Option 3: Use Environment Variables

Set environment variables (useful for production):

**Windows PowerShell:**
```powershell
$env:DB_HOST = "localhost"
$env:DB_NAME = "your_database"
$env:DB_USER = "root"
$env:DB_PASSWORD = ""
```

**Windows CMD:**
```cmd
set DB_HOST=localhost
set DB_NAME=your_database
set DB_USER=root
set DB_PASSWORD=
```

Then the service will use these automatically.

## After Configuration

1. **Test the connection:**
```bash
python check_database.py
```

2. **Restart the service:**
   - Stop the current service (Ctrl+C if running in terminal)
   - Start again: `python app.py`

3. **Train models:**
```powershell
Invoke-WebRequest -Uri http://localhost:5000/train -Method POST
```

## Quick Check: What's Your Database Name?

Run this in your PHP application or check `config/database.php`:

```php
// In config/database.php, look for:
private $db_name = 'YOUR_DATABASE_NAME_HERE';
```

Use that name in `ml_service/app.py`.

## Troubleshooting

### "Access denied for user"
- **Solution**: Check username and password
- For XAMPP, usually `root` with empty password

### "Unknown database"
- **Solution**: Database doesn't exist
- Create it in phpMyAdmin or import your database

### "Can't connect to MySQL server"
- **Solution**: Make sure XAMPP MySQL is running
- Check XAMPP Control Panel

### "Insufficient data"
- **Solution**: You need:
  - At least some orders in the database
  - At least some active products
  - (Optional) User searches and views

## Need Help?

1. Check your PHP `config/database.php` for the correct credentials
2. Make sure XAMPP MySQL is running
3. Verify the database exists in phpMyAdmin
4. Update `ml_service/app.py` with correct credentials
5. Test with `python check_database.py`

