"""
Flask API for Product Recommendations
Uses scikit-learn for collaborative filtering and content-based recommendations
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import pickle
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from PHP

# Database configuration (match your PHP config)
# For local XAMPP, you might need to use 'root' with empty password
# For production, use the credentials from config/database.php
import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'u520834156_dbBagoMerkado'),
    'user': os.getenv('DB_USER', 'u520834156_userBMerkado25'),
    'password': os.getenv('DB_PASSWORD', 's;h7TLSLl?4')
}

# Try local XAMPP config if production fails
DB_CONFIG_LOCAL = {
    'host': 'localhost',
    'database': 'u520834156_dbBagoMerkado',  # or your local database name
    'user': 'root',
    'password': '',  # XAMPP default is empty
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'use_unicode': True
}

# Model storage
MODELS_DIR = 'models'
os.makedirs(MODELS_DIR, exist_ok=True)

class RecommendationService:
    def __init__(self):
        self.db_conn = None
        self.svd_model = None
        self.tfidf_vectorizer = None
        self.product_features = None
        self.user_item_matrix = None
        self.user_to_idx = {}
        self.product_to_idx = {}
        self.model_trained_at = None
        
    def get_db_connection(self):
        """Get database connection"""
        try:
            if self.db_conn is None or not self.db_conn.is_connected():
                try:
                    # Try production config first
                    self.db_conn = mysql.connector.connect(**DB_CONFIG)
                except Error:
                    # Fallback to local XAMPP config
                    print("Trying local XAMPP database configuration...")
                    try:
                        # Add connection arguments to handle collation issues
                        local_config = DB_CONFIG_LOCAL.copy()
                        self.db_conn = mysql.connector.connect(
                            host=local_config['host'],
                            database=local_config['database'],
                            user=local_config['user'],
                            password=local_config['password'],
                            charset='utf8mb4',
                            collation='utf8mb4_unicode_ci',
                            use_unicode=True,
                            sql_mode=''
                        )
                    except Error as e:
                        print(f"Error connecting to database: {e}")
                        print("\nPlease check:")
                        print("1. MySQL/XAMPP is running")
                        print("2. Database credentials in app.py are correct")
                        print("3. Database exists and is accessible")
                        return None
            return self.db_conn
        except Error as e:
            print(f"Error connecting to database: {e}")
            return None
    
    def load_training_data(self):
        """Load data from database for training"""
        conn = self.get_db_connection()
        if not conn:
            return None, None, None
        
        cursor = conn.cursor(dictionary=True)
        
        # Get user-item interactions (purchases)
        cursor.execute("""
            SELECT customer_id, product_id, SUM(quantity) as total_quantity, COUNT(*) as order_count
            FROM orders
            WHERE status IN ('delivered', 'completed', 'confirmed', 'preparing', 'packed', 'for_pickup', 'out_for_delivery')
            AND payment_status = 'paid'
            GROUP BY customer_id, product_id
        """)
        interactions = cursor.fetchall()
        
        # Get product features
        cursor.execute("""
            SELECT p.product_id, p.name, p.description, p.category_id, p.price,
                   c.name as category_name,
                   COALESCE(AVG(r.rating), 0) as avg_rating,
                   COUNT(DISTINCT o.orders_id) as purchase_count
            FROM product p
            LEFT JOIN category c ON p.category_id = c.category_id
            LEFT JOIN orders o ON p.product_id = o.product_id 
                AND o.status IN ('delivered', 'completed', 'confirmed')
            LEFT JOIN rating r ON o.orders_id = r.orders_id
            WHERE p.status = 'active'
            AND (p.moderation_status = 'approved' OR p.moderation_status IS NULL)
            GROUP BY p.product_id
        """)
        products = cursor.fetchall()
        
        # Get user searches
        cursor.execute("""
            SELECT customer_id, search_term, category_id, COUNT(*) as search_count
            FROM user_searches
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 90 DAY)
            GROUP BY customer_id, search_term, category_id
        """)
        searches = cursor.fetchall()
        
        cursor.close()
        
        return interactions, products, searches
    
    def build_user_item_matrix(self, interactions):
        """Build user-item interaction matrix"""
        if not interactions:
            return None, {}, {}
        
        # Get unique users and products
        users = sorted(set([i['customer_id'] for i in interactions]))
        products = sorted(set([i['product_id'] for i in interactions]))
        
        user_to_idx = {user: idx for idx, user in enumerate(users)}
        product_to_idx = {product: idx for idx, product in enumerate(products)}
        
        # Build matrix (users x products)
        matrix = np.zeros((len(users), len(products)))
        
        for interaction in interactions:
            user_idx = user_to_idx[interaction['customer_id']]
            product_idx = product_to_idx[interaction['product_id']]
            # Weight: quantity + order count
            score = interaction['total_quantity'] + (interaction['order_count'] * 2)
            matrix[user_idx, product_idx] = score
        
        return matrix, user_to_idx, product_to_idx
    
    def train_collaborative_filtering(self, interactions):
        """Train SVD model for collaborative filtering"""
        try:
            matrix, user_to_idx, product_to_idx = self.build_user_item_matrix(interactions)
            
            if matrix is None or matrix.size == 0:
                return False
            
            # Use TruncatedSVD for dimensionality reduction
            n_components = min(50, min(matrix.shape) - 1)  # Number of latent factors
            if n_components < 1:
                return False
            
            self.svd_model = TruncatedSVD(n_components=n_components, random_state=42)
            self.user_item_matrix = matrix
            self.user_to_idx = user_to_idx
            self.product_to_idx = product_to_idx
            
            # Fit the model
            self.svd_model.fit(matrix)
            
            return True
        except Exception as e:
            print(f"Error in train_collaborative_filtering: {e}")
            # Initialize empty attributes if training fails
            self.user_to_idx = {}
            self.product_to_idx = {}
            return False
    
    def train_content_based(self, products):
        """Train TF-IDF model for content-based recommendations"""
        if not products:
            return False
        
        # Combine product name and description
        product_texts = []
        for product in products:
            text = f"{product['name']} {product.get('description', '')} {product.get('category_name', '')}"
            product_texts.append(text)
        
        # Create TF-IDF vectors
        self.tfidf_vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        product_vectors = self.tfidf_vectorizer.fit_transform(product_texts)
        
        # Store product features
        self.product_features = {
            products[i]['product_id']: product_vectors[i] 
            for i in range(len(products))
        }
        
        return True
    
    def train_models(self):
        """Train all recommendation models"""
        print("Loading training data...")
        interactions, products, searches = self.load_training_data()
        
        if not interactions and not products:
            print("No data available for training")
            return False
        
        print("Training collaborative filtering model...")
        cf_success = self.train_collaborative_filtering(interactions)
        
        print("Training content-based model...")
        cb_success = self.train_content_based(products)
        
        if cf_success or cb_success:
            self.model_trained_at = datetime.now()
            self.save_models()
            print("Models trained and saved successfully!")
            return True
        
        return False
    
    def save_models(self):
        """Save trained models to disk"""
        models = {
            'svd_model': self.svd_model,
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'product_features': self.product_features,
            'user_item_matrix': self.user_item_matrix,
            'user_to_idx': self.user_to_idx,
            'product_to_idx': self.product_to_idx,
            'trained_at': self.model_trained_at.isoformat() if self.model_trained_at else None
        }
        
        with open(f'{MODELS_DIR}/recommendation_models.pkl', 'wb') as f:
            pickle.dump(models, f)
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            with open(f'{MODELS_DIR}/recommendation_models.pkl', 'rb') as f:
                models = pickle.load(f)
            
            self.svd_model = models.get('svd_model')
            self.tfidf_vectorizer = models.get('tfidf_vectorizer')
            self.product_features = models.get('product_features', {})
            self.user_item_matrix = models.get('user_item_matrix')
            self.user_to_idx = models.get('user_to_idx', {})
            self.product_to_idx = models.get('product_to_idx', {})
            
            if models.get('trained_at'):
                self.model_trained_at = datetime.fromisoformat(models['trained_at'])
            
            # Check if models are stale (older than 7 days) - retrain if needed
            if self.model_trained_at:
                days_old = (datetime.now() - self.model_trained_at).days
                if days_old > 7:
                    print(f"Models are {days_old} days old. Consider retraining.")
            
            return True
        except FileNotFoundError:
            print("No saved models found. Training new models...")
            # Auto-train on first startup (useful for Heroku)
            return self.train_models()
        except Exception as e:
            print(f"Error loading models: {e}")
            print("Attempting to train new models...")
            return self.train_models()
    
    def get_collaborative_recommendations(self, customer_id, n_recommendations=10):
        """Get recommendations using collaborative filtering"""
        if not self.svd_model or customer_id not in self.user_to_idx:
            return []
        
        user_idx = self.user_to_idx[customer_id]
        user_vector = self.user_item_matrix[user_idx:user_idx+1]
        
        # Transform to latent space
        user_latent = self.svd_model.transform(user_vector)
        
        # Transform all users to latent space
        all_users_latent = self.svd_model.transform(self.user_item_matrix)
        
        # Find similar users
        similarities = cosine_similarity(user_latent, all_users_latent)[0]
        similar_users_idx = np.argsort(similarities)[::-1][1:11]  # Top 10 similar users
        
        # Get products liked by similar users
        product_scores = {}
        for similar_user_idx in similar_users_idx:
            user_products = np.where(self.user_item_matrix[similar_user_idx] > 0)[0]
            for product_idx in user_products:
                product_id = list(self.product_to_idx.keys())[list(self.product_to_idx.values()).index(product_idx)]
                if product_id not in product_scores:
                    product_scores[product_id] = 0
                product_scores[product_id] += similarities[similar_user_idx] * self.user_item_matrix[similar_user_idx, product_idx]
        
        # Sort by score and return top N
        sorted_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)
        return [product_id for product_id, score in sorted_products[:n_recommendations]]
    
    def get_content_based_recommendations(self, customer_id, n_recommendations=10):
        """Get recommendations based on user's viewed/purchased products"""
        conn = self.get_db_connection()
        if not conn or not self.product_features:
            return []
        
        cursor = conn.cursor(dictionary=True)
        
        # Get user's interacted products
        cursor.execute("""
            SELECT DISTINCT product_id FROM (
                SELECT product_id FROM orders WHERE customer_id = %s
                UNION
                SELECT product_id FROM product_views WHERE customer_id = %s
            ) as interacted
            LIMIT 20
        """, (customer_id, customer_id))
        user_products = [row['product_id'] for row in cursor.fetchall()]
        cursor.close()
        
        if not user_products:
            return []
        
        # Get average vector of user's products
        user_product_vectors = []
        for product_id in user_products:
            if product_id in self.product_features:
                user_product_vectors.append(self.product_features[product_id])
        
        if not user_product_vectors:
            return []
        
        # Average the vectors
        from scipy.sparse import vstack
        user_vector = vstack(user_product_vectors).mean(axis=0)
        
        # Find similar products
        product_scores = {}
        for product_id, product_vector in self.product_features.items():
            if product_id not in user_products:
                similarity = cosine_similarity(user_vector, product_vector)[0][0]
                product_scores[product_id] = similarity
        
        # Sort and return top N
        sorted_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)
        return [product_id for product_id, score in sorted_products[:n_recommendations]]
    
    def get_hybrid_recommendations(self, customer_id, n_recommendations=10):
        """Combine collaborative and content-based recommendations"""
        cf_recs = self.get_collaborative_recommendations(customer_id, n_recommendations * 2)
        cb_recs = self.get_content_based_recommendations(customer_id, n_recommendations * 2)
        
        # Combine and deduplicate
        combined = {}
        
        # Weight collaborative filtering more
        for idx, product_id in enumerate(cf_recs):
            combined[product_id] = combined.get(product_id, 0) + (len(cf_recs) - idx) * 2
        
        for idx, product_id in enumerate(cb_recs):
            combined[product_id] = combined.get(product_id, 0) + (len(cb_recs) - idx)
        
        # Sort by score
        sorted_products = sorted(combined.items(), key=lambda x: x[1], reverse=True)
        return [product_id for product_id, score in sorted_products[:n_recommendations]]

# Initialize service
recommendation_service = RecommendationService()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'recommendation-api'})

@app.route('/train', methods=['POST'])
def train_models():
    """Train recommendation models"""
    try:
        success = recommendation_service.train_models()
        if success:
            return jsonify({
                'success': True,
                'message': 'Models trained successfully',
                'trained_at': recommendation_service.model_trained_at.isoformat() if recommendation_service.model_trained_at else None
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to train models - insufficient data'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error training models: {str(e)}'
        }), 500

@app.route('/recommendations/<int:customer_id>', methods=['GET'])
def get_recommendations(customer_id):
    """Get product recommendations for a customer"""
    try:
        # Load models if not loaded
        if recommendation_service.svd_model is None:
            if not recommendation_service.load_models():
                return jsonify({
                    'success': False,
                    'message': 'Models not available. Please train models first.',
                    'products': []
                }), 503
        
        # Check if models are stale (older than 7 days)
        if recommendation_service.model_trained_at:
            days_old = (datetime.now() - recommendation_service.model_trained_at).days
            if days_old > 7:
                # Models are stale, but still return recommendations
                pass
        
        limit = int(request.args.get('limit', 10))
        method = request.args.get('method', 'hybrid')  # 'collaborative', 'content', or 'hybrid'
        
        if method == 'collaborative':
            product_ids = recommendation_service.get_collaborative_recommendations(customer_id, limit)
        elif method == 'content':
            product_ids = recommendation_service.get_content_based_recommendations(customer_id, limit)
        else:  # hybrid
            product_ids = recommendation_service.get_hybrid_recommendations(customer_id, limit)
        
        # Get product details from database
        if product_ids:
            conn = recommendation_service.get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                placeholders = ','.join(['%s'] * len(product_ids))
                cursor.execute(f"""
                    SELECT p.*, 
                           COALESCE(MIN(ps.price), p.price) as min_price,
                           c.name as category_name,
                           s.business_name, s.firstname, s.lastname
                    FROM product p
                    LEFT JOIN product_size ps ON p.product_id = ps.product_id
                    LEFT JOIN category c ON p.category_id = c.category_id
                    LEFT JOIN seller s ON p.seller_id = s.seller_id
                    WHERE p.product_id IN ({placeholders})
                    AND p.status = 'active'
                    GROUP BY p.product_id
                    ORDER BY FIELD(p.product_id, {placeholders})
                """, product_ids + product_ids)
                products = cursor.fetchall()
                cursor.close()
            else:
                products = []
        else:
            products = []
        
        return jsonify({
            'success': True,
            'products': products,
            'count': len(products),
            'method': method
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting recommendations: {str(e)}',
            'products': []
        }), 500

@app.route('/similar/<int:product_id>', methods=['GET'])
def get_similar_products(product_id):
    """Get products similar to a given product"""
    try:
        if not recommendation_service.product_features:
            recommendation_service.load_models()
        
        if product_id not in recommendation_service.product_features:
            return jsonify({
                'success': False,
                'message': 'Product not found',
                'products': []
            }), 404
        
        product_vector = recommendation_service.product_features[product_id]
        limit = int(request.args.get('limit', 10))
        
        # Find similar products
        product_scores = {}
        for other_product_id, other_vector in recommendation_service.product_features.items():
            if other_product_id != product_id:
                similarity = cosine_similarity(product_vector, other_vector)[0][0]
                product_scores[other_product_id] = similarity
        
        # Sort and get top N
        sorted_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)
        similar_product_ids = [pid for pid, score in sorted_products[:limit]]
        
        # Get product details
        if similar_product_ids:
            conn = recommendation_service.get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                placeholders = ','.join(['%s'] * len(similar_product_ids))
                cursor.execute(f"""
                    SELECT p.*, 
                           COALESCE(MIN(ps.price), p.price) as min_price,
                           c.name as category_name
                    FROM product p
                    LEFT JOIN product_size ps ON p.product_id = ps.product_id
                    LEFT JOIN category c ON p.category_id = c.category_id
                    WHERE p.product_id IN ({placeholders})
                    AND p.status = 'active'
                    GROUP BY p.product_id
                """, similar_product_ids)
                products = cursor.fetchall()
                cursor.close()
            else:
                products = []
        else:
            products = []
        
        return jsonify({
            'success': True,
            'products': products,
            'count': len(products)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting similar products: {str(e)}',
            'products': []
        }), 500

if __name__ == '__main__':
    # Load models on startup
    print("Loading recommendation models...")
    recommendation_service.load_models()
    
    # Run Flask app
    print("Starting Flask recommendation service on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

