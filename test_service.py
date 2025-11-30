"""Quick test to verify Flask service can start"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing imports...")
    from flask import Flask
    from flask_cors import CORS
    import mysql.connector
    import numpy as np
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    print("✓ All imports successful!")
    
    print("\nTesting database connection...")
    from app import DB_CONFIG, DB_CONFIG_LOCAL
    
    # Try production config first
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            print("✓ Database connection successful (production config)!")
            conn.close()
        else:
            raise Exception("Connection failed")
    except Exception as e:
        print(f"✗ Production config failed: {e}")
        print("Trying local XAMPP config (root/empty password)...")
        try:
            conn = mysql.connector.connect(**DB_CONFIG_LOCAL)
            if conn.is_connected():
                print("✓ Database connection successful (local XAMPP config)!")
                print("  Note: Update DB_CONFIG in app.py to use local config")
                conn.close()
            else:
                raise Exception("Connection failed")
        except Exception as e2:
            print(f"✗ Local config also failed: {e2}")
            print("\nPlease check:")
            print("1. MySQL/XAMPP is running")
            print("2. Database exists")
            print("3. Update DB_CONFIG in app.py with correct credentials")
        
    print("\nTesting Flask app creation...")
    app = Flask(__name__)
    CORS(app)
    print("✓ Flask app created successfully!")
    
    print("\n✅ All tests passed! Service should work.")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nPlease install dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

