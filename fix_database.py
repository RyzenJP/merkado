"""Interactive script to help configure database"""
import os

print("="*60)
print("ML Service Database Configuration Helper")
print("="*60)
print()

# Get database info from user
print("Please provide your database information:")
print("(Press Enter to use defaults)")
print()

host = input("Database Host [localhost]: ").strip() or "localhost"
database = input("Database Name: ").strip()
if not database:
    print("❌ Database name is required!")
    exit(1)

user = input("Database User [root]: ").strip() or "root"
password = input("Database Password []: ").strip()

print()
print("Testing connection...")

# Test connection
try:
    import mysql.connector
    from mysql.connector import Error
    
    config = {
        'host': host,
        'database': database,
        'user': user,
        'password': password
    }
    
    conn = mysql.connector.connect(**config)
    if conn.is_connected():
        print("✅ Connection successful!")
        
        cursor = conn.cursor(dictionary=True)
        
        # Check data
        cursor.execute("SELECT COUNT(*) as count FROM orders WHERE status IN ('delivered', 'completed', 'confirmed', 'preparing', 'packed', 'for_pickup', 'out_for_delivery') AND payment_status = 'paid'")
        orders = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) as count FROM product WHERE status = 'active' AND (moderation_status = 'approved' OR moderation_status IS NULL)")
        products = cursor.fetchone()
        
        print(f"📦 Orders found: {orders['count']}")
        print(f"🛍️  Active products: {products['count']}")
        
        if orders['count'] > 0 and products['count'] > 0:
            print("\n✅ Sufficient data for training!")
        else:
            print("\n⚠️  Warning: Limited data available")
        
        cursor.close()
        conn.close()
        
        # Update app.py
        print("\n" + "="*60)
        print("Updating app.py...")
        
        app_py_path = os.path.join(os.path.dirname(__file__), 'app.py')
        
        with open(app_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace DB_CONFIG
        new_config = f"""DB_CONFIG = {{
    'host': '{host}',
    'database': '{database}',
    'user': '{user}',
    'password': '{password}'
}}"""
        
        # Find and replace DB_CONFIG block
        import re
        pattern = r"DB_CONFIG = \{[^}]+\}"
        content = re.sub(pattern, new_config, content, flags=re.DOTALL)
        
        with open(app_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ app.py updated successfully!")
        print("\nNext steps:")
        print("1. Restart the Flask service")
        print("2. Train models: Invoke-WebRequest -Uri http://localhost:5000/train -Method POST")
        
    else:
        print("❌ Connection failed")
        
except ImportError:
    print("❌ mysql-connector-python not installed")
    print("Run: pip install mysql-connector-python")
except Error as e:
    print(f"❌ Connection error: {e}")
    print("\nPlease check:")
    print("1. MySQL/XAMPP is running")
    print("2. Database credentials are correct")
    print("3. Database exists")

