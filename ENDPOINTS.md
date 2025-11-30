# 📡 ML Service API Endpoints

## ✅ Endpoints Already Built-In!

All endpoints are **already defined** in `app.py`. When you deploy to Heroku, they automatically become available at:

**Base URL**: `https://your-app-name.herokuapp.com`

---

## Available Endpoints

### 1. **Health Check**
```
GET /health
```

**Purpose**: Check if service is running

**Example**:
```bash
curl https://your-app-name.herokuapp.com/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "recommendation-api"
}
```

---

### 2. **Get Recommendations** ⭐ (Main Endpoint)
```
GET /recommendations/<customer_id>?limit=10&method=hybrid
```

**Purpose**: Get personalized product recommendations for a customer

**Parameters**:
- `customer_id` (path): Customer ID (required)
- `limit` (query): Number of recommendations (default: 10)
- `method` (query): `'collaborative'`, `'content'`, or `'hybrid'` (default: `'hybrid'`)

**Example**:
```bash
curl https://your-app-name.herokuapp.com/recommendations/123?limit=10&method=hybrid
```

**Response**:
```json
{
  "success": true,
  "products": [
    {
      "product_id": 456,
      "name": "Gaming Mouse",
      "price": 1500,
      "image": "mouse.jpg",
      "category_name": "Electronics"
    },
    ...
  ],
  "count": 10,
  "method": "hybrid"
}
```

**This is the endpoint your PHP app calls!**

---

### 3. **Train Models**
```
POST /train
```

**Purpose**: Train/retrain the ML models

**Example**:
```bash
curl -X POST https://your-app-name.herokuapp.com/train
```

**Response**:
```json
{
  "success": true,
  "message": "Models trained successfully",
  "trained_at": "2024-01-15T10:30:00"
}
```

---

### 4. **Get Similar Products**
```
GET /similar/<product_id>?limit=10
```

**Purpose**: Get products similar to a given product

**Parameters**:
- `product_id` (path): Product ID (required)
- `limit` (query): Number of similar products (default: 10)

**Example**:
```bash
curl https://your-app-name.herokuapp.com/similar/456?limit=5
```

**Response**:
```json
{
  "success": true,
  "products": [...],
  "count": 5
}
```

---

## How PHP Calls It

Your PHP code in `RecommendationEngine.php` already calls the main endpoint:

```php
// This is what happens automatically:
$url = "https://your-app-name.herokuapp.com/recommendations/{$customer_id}?limit={$limit}&method=hybrid";

// PHP makes GET request to this endpoint
$response = file_get_contents($url);

// Returns JSON with recommendations
```

---

## No Additional Setup Needed!

✅ **Endpoints are already defined** in `app.py`  
✅ **Automatically available** when deployed to Heroku  
✅ **PHP already configured** to call the right endpoint  
✅ **No code changes needed!**

---

## Testing Endpoints Locally

Before deploying to Heroku, test locally:

```bash
# Start service
python app.py

# Test health
curl http://localhost:5000/health

# Test recommendations
curl http://localhost:5000/recommendations/1?limit=10

# Train models
curl -X POST http://localhost:5000/train
```

---

## After Deploying to Heroku

Just replace `localhost:5000` with your Heroku URL:

```bash
# Health check
curl https://your-app-name.herokuapp.com/health

# Get recommendations
curl https://your-app-name.herokuapp.com/recommendations/1?limit=10

# Train models
curl -X POST https://your-app-name.herokuapp.com/train
```

**That's it! The endpoints work automatically!** 🚀

