# 🚀 Deploying ML Service to Heroku

## Overview

This guide explains how to deploy the ML recommendation service to Heroku and integrate it with your PHP application.

## Architecture

```
┌─────────────────────────────────────┐
│  PHP Application (Your Server)     │
│  - Makes HTTP request to Heroku     │
│  - Falls back to PHP engine if fail │
└──────────────┬──────────────────────┘
               │ HTTPS Request
               ↓
┌─────────────────────────────────────┐
│  Heroku ML Service                   │
│  - Flask app running on dyno         │
│  - Trains models on startup          │
│  - Provides recommendations API       │
└─────────────────────────────────────┘
```

## Step 1: Prepare for Deployment

### 1.1 Update Database Configuration

The ML service needs to connect to your database from Heroku. Update `app.py`:

```python
import os

# Use environment variables for database config
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'u520834156_dbBagoMerkado'),
    'user': os.getenv('DB_USER', 'u520834156_userBMerkado25'),
    'password': os.getenv('DB_PASSWORD', 's;h7TLSLl?4')
}
```

**Important**: Make sure your database allows remote connections from Heroku's IP addresses.

### 1.2 Update Model Storage

Heroku's filesystem is ephemeral (resets on restart). We'll train models on startup:

```python
# In app.py, modify load_models() to auto-train if no models exist
def load_models(self):
    try:
        # Try to load existing models
        with open(f'{MODELS_DIR}/recommendation_models.pkl', 'rb') as f:
            models = pickle.load(f)
        # ... load models
        return True
    except FileNotFoundError:
        # Auto-train on first startup
        print("No models found. Training new models...")
        return self.train_models()
```

## Step 2: Deploy to Heroku

### 2.1 Install Heroku CLI

Download from: https://devcenter.heroku.com/articles/heroku-cli

### 2.2 Login to Heroku

```bash
heroku login
```

### 2.3 Create Heroku App

```bash
cd ml_service
heroku create your-ml-service-name
# Example: heroku create bagomerkado-ml-service
```

### 2.4 Set Environment Variables

```bash
# Database configuration
heroku config:set DB_HOST=your_database_host
heroku config:set DB_NAME=u520834156_dbBagoMerkado
heroku config:set DB_USER=u520834156_userBMerkado25
heroku config:set DB_PASSWORD=your_database_password

# Optional: Set ML service URL (for PHP integration)
heroku config:set ML_SERVICE_URL=https://your-ml-service-name.herokuapp.com
```

### 2.5 Deploy

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit"

# Deploy to Heroku
git push heroku main
# or: git push heroku master
```

### 2.6 Train Models (First Time)

After deployment, train the models:

```bash
heroku run python -c "from app import recommendation_service; recommendation_service.train_models()"
```

Or use the API:

```bash
curl -X POST https://your-ml-service-name.herokuapp.com/train
```

## Step 3: Update PHP Integration

### 3.1 Update RecommendationEngine.php

Update the `getMLRecommendations` method to use Heroku URL:

```php
private function getMLRecommendations($customer_id, $limit = 10) {
    try {
        // Get Heroku URL from environment or config
        $ml_service_url = getenv('ML_RECOMMENDATION_URL') 
            ?: 'https://your-ml-service-name.herokuapp.com';
        
        $url = "{$ml_service_url}/recommendations/{$customer_id}?limit={$limit}&method=hybrid";
        
        $context = stream_context_create([
            'http' => [
                'method' => 'GET',
                'timeout' => 5, // Increased timeout for Heroku
                'ignore_errors' => true,
                'header' => [
                    'Accept: application/json',
                    'User-Agent: PHP-RecommendationEngine/1.0'
                ]
            ]
        ]);
        
        $response = @file_get_contents($url, false, $context);
        
        if ($response === false) {
            return []; // ML service unavailable, will fallback to PHP recommendations
        }
        
        $data = json_decode($response, true);
        
        if (isset($data['success']) && $data['success'] && !empty($data['products'])) {
            $recommendations = [];
            foreach ($data['products'] as $product) {
                $product_id = $product['product_id'];
                // ML recommendations get high score (90-100 range)
                $recommendations[$product_id] = 95;
            }
            return $recommendations;
        }
    } catch (Exception $e) {
        error_log("ML recommendation error: " . $e->getMessage());
    }
    
    return []; // Fallback
}
```

### 3.2 Set Environment Variable in PHP

In your PHP application, set the ML service URL:

**Option A: In `config/database.php` or `.env` file:**
```php
// Add to config/database.php
define('ML_RECOMMENDATION_URL', 'https://your-ml-service-name.herokuapp.com');
```

**Option B: In server environment variables:**
```bash
# In your server's .htaccess or php.ini
SetEnv ML_RECOMMENDATION_URL https://your-ml-service-name.herokuapp.com
```

**Option C: In `config/RecommendationEngine.php`:**
```php
private function getMLRecommendations($customer_id, $limit = 10) {
    // Hardcode for now, or use config
    $ml_service_url = 'https://your-ml-service-name.herokuapp.com';
    // ... rest of code
}
```

## Step 4: How It Works

### 4.1 Request Flow

```
1. Customer visits products page
   ↓
2. PHP RecommendationEngine.getRecommendations() called
   ↓
3. Tries ML service first (Heroku)
   ├─ Success → Returns ML recommendations
   └─ Failure → Falls back to PHP engine
   ↓
4. Displays recommendations to customer
```

### 4.2 Automatic Fallback

The PHP code automatically handles:
- ✅ Heroku service unavailable → Uses PHP engine
- ✅ Heroku timeout → Uses PHP engine
- ✅ Heroku error → Uses PHP engine
- ✅ No ML recommendations → Uses PHP engine

**Your app always works, even if Heroku is down!**

## Step 5: Model Retraining

### 5.1 Manual Retraining

```bash
# Via Heroku CLI
heroku run python -c "from app import recommendation_service; recommendation_service.train_models()"

# Via API
curl -X POST https://your-ml-service-name.herokuapp.com/train
```

### 5.2 Automatic Retraining (Recommended)

Set up a scheduled task using Heroku Scheduler:

1. Go to Heroku Dashboard → Your App → Scheduler
2. Add job:
   - **Command**: `python -c "from app import recommendation_service; recommendation_service.train_models()"`
   - **Frequency**: Daily or Weekly

Or use a cron service like EasyCron to call:
```
POST https://your-ml-service-name.herokuapp.com/train
```

## Step 6: Monitoring

### 6.1 Check Service Status

```bash
# Health check
curl https://your-ml-service-name.herokuapp.com/health

# View logs
heroku logs --tail
```

### 6.2 Monitor Performance

- **Heroku Dashboard**: View dyno usage, response times
- **Logs**: Check for errors, training status
- **PHP Logs**: Monitor ML service calls and fallbacks

## Important Considerations

### Database Access

⚠️ **Your database must allow connections from Heroku IPs**

1. **Whitelist Heroku IPs** (if using firewall)
2. **Use SSL connection** (recommended)
3. **Consider using a database connection pooler** (PgBouncer, etc.)

### Model Storage

- Models are stored in `/app/models/` on Heroku
- Models are **ephemeral** - they reset on dyno restart
- **Solution**: Auto-train on startup (already implemented)

### Performance

- **Cold starts**: First request after inactivity may be slow (30+ seconds)
- **Solution**: Use Heroku Scheduler to ping the service every 10 minutes
- **Or**: Upgrade to a paid dyno that doesn't sleep

### Cost

- **Free tier**: 550-1000 hours/month (dyno sleeps after 30 min inactivity)
- **Hobby tier ($7/month)**: Always-on, better for production

## Troubleshooting

### Issue: "Cannot connect to database"
- Check database allows remote connections
- Verify environment variables are set correctly
- Test connection: `heroku run python -c "from app import recommendation_service; conn = recommendation_service.get_db_connection(); print('Connected!' if conn else 'Failed')"`

### Issue: "Models not found"
- Models are auto-trained on first request
- Or manually train: `curl -X POST https://your-app.herokuapp.com/train`

### Issue: "Service timeout"
- Increase timeout in PHP: `'timeout' => 10`
- Check Heroku logs for errors
- Consider upgrading dyno size

### Issue: "Cold start too slow"
- Use Heroku Scheduler to keep dyno awake
- Or upgrade to paid tier

## Quick Reference

```bash
# Deploy
git push heroku main

# View logs
heroku logs --tail

# Train models
curl -X POST https://your-app.herokuapp.com/train

# Test recommendations
curl https://your-app.herokuapp.com/recommendations/1?limit=10

# Set config
heroku config:set DB_HOST=your_host

# Open app
heroku open
```

## Summary

1. ✅ **Deploy to Heroku**: Push code, set environment variables
2. ✅ **Train Models**: Run training on first deployment
3. ✅ **Update PHP**: Point `RecommendationEngine` to Heroku URL
4. ✅ **Automatic Fallback**: PHP engine works if Heroku is down
5. ✅ **Schedule Retraining**: Set up automatic model updates

Your ML service will work seamlessly with your PHP application! 🚀

