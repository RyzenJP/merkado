# ML Recommendation Service Integration Guide

## Overview

This Flask service provides advanced ML-based product recommendations using:
- **Collaborative Filtering** (SVD matrix factorization)
- **Content-Based Filtering** (TF-IDF + cosine similarity)
- **Hybrid Approach** (combines both methods)

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd ml_service
pip install -r requirements.txt
```

### 2. Configure Database

Update `DB_CONFIG` in `app.py` to match your database credentials.

### 3. Train Initial Models

```bash
# Start the Flask service
python app.py

# In another terminal, train models
curl -X POST http://localhost:5000/train
```

### 4. Integration with PHP

Update your PHP RecommendationEngine to call Flask API:

```php
// In config/RecommendationEngine.php, add this method:

private function getMLRecommendations($customer_id, $limit = 10) {
    try {
        $url = "http://localhost:5000/recommendations/{$customer_id}?limit={$limit}&method=hybrid";
        $response = @file_get_contents($url);
        
        if ($response === false) {
            return []; // Fallback to PHP-based recommendations
        }
        
        $data = json_decode($response, true);
        if ($data['success'] && !empty($data['products'])) {
            $recommendations = [];
            foreach ($data['products'] as $product) {
                $recommendations[$product['product_id']] = 90; // High score for ML recommendations
            }
            return $recommendations;
        }
    } catch (Exception $e) {
        error_log("ML recommendation error: " . $e->getMessage());
    }
    
    return []; // Fallback
}
```

## API Endpoints

### GET `/recommendations/<customer_id>`
Get personalized recommendations for a customer.

**Parameters:**
- `limit` (optional): Number of recommendations (default: 10)
- `method` (optional): 'collaborative', 'content', or 'hybrid' (default: 'hybrid')

**Example:**
```
GET http://localhost:5000/recommendations/123?limit=10&method=hybrid
```

### GET `/similar/<product_id>`
Get products similar to a given product.

**Parameters:**
- `limit` (optional): Number of similar products (default: 10)

**Example:**
```
GET http://localhost:5000/similar/456?limit=5
```

### POST `/train`
Train/retrain the recommendation models.

**Example:**
```
POST http://localhost:5000/train
```

## Model Retraining

Models should be retrained periodically (recommended: weekly or when significant new data is available).

You can set up a cron job:
```bash
# Run every Sunday at 2 AM
0 2 * * 0 curl -X POST http://localhost:5000/train
```

## Performance

- **Training Time**: ~1-5 minutes (depends on data size)
- **Inference Time**: ~50-200ms per request
- **Memory Usage**: ~100-500MB (depends on data size)

## Future Enhancements

1. **Deep Learning Models**: Upgrade to Neural Collaborative Filtering
2. **Real-time Learning**: Update models incrementally as new data arrives
3. **A/B Testing**: Compare different recommendation strategies
4. **Explainability**: Add reasons why products are recommended

