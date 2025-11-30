# Machine Learning Recommendation Service

## Current Implementation

The current recommendation system uses **PHP-based algorithms**:
- **Collaborative Filtering**: Finds similar customers and recommends products they bought
- **Content-Based Filtering**: Recommends products similar to what user viewed/searched
- **Hybrid Approach**: Combines multiple signals (purchases, views, searches)

## Advanced ML Option

For more sophisticated machine learning, we can integrate a **Python/Flask service** with these options:

Lightweight ML (Recommended for Start)
- **Framework**: Flask + scikit-learn
- **Models**:
  - **Matrix Factorization** (SVD/NMF) for collaborative filtering
  - **TF-IDF + Cosine Similarity** for content-based recommendations
  - **XGBoost** for ranking products
- **Pros**: Fast, easy to deploy, good for small-medium datasets
- **Cons**: Less sophisticated than deep learning





## Implementation Plan

1. **Python Flask API** that PHP calls via HTTP
2. **Model Training Script** (runs periodically to retrain)
3. **Real-time Inference** (fast predictions)
4. **Data Pipeline** (exports data from MySQL to format ML models need)

Would you like me to implement the Flask + scikit-learn service?

