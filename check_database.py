"""Check database connection and data availability"""
import mysql.connector
from mysql.connector import Error

# Try production config
DB_CONFIG = {
    'host': 'localhost',
    'database': 'u520834156_dbBagoMerkado',
    'user': 'u520834156_userBMerkado25',
    'password': 's;h7TLSLl?4'
}

# Try local XAMPP config
DB_CONFIG_LOCAL = {
    'host': 'localhost',
    'database': 'u520834156_dbBagoMerkado',
    'user': 'root',
    'password': '',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def check_database(config, config_name):
    print(f"\n{'='*50}")
    print(f"Testing {config_name} configuration...")
    print(f"{'='*50}")
    
    try:
        # Handle collation for local config
        if config_name == "Local XAMPP":
            conn = mysql.connector.connect(
                host=config['host'],
                database=config['database'],
                user=config['user'],
                password=config['password'],
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci',
                use_unicode=True,
                sql_mode=''
            )
        else:
            conn = mysql.connector.connect(**config)
        
        if conn.is_connected():
            print(f"✅ Connected to database: {config['database']}")
            
            cursor = conn.cursor(dictionary=True)
            
            # Check orders
            cursor.execute("SELECT COUNT(*) as count FROM orders WHERE status IN ('delivered', 'completed', 'confirmed', 'preparing', 'packed', 'for_pickup', 'out_for_delivery') AND payment_status = 'paid'")
            orders = cursor.fetchone()
            print(f"📦 Orders: {orders['count']}")
            
            # Check products
            cursor.execute("SELECT COUNT(*) as count FROM product WHERE status = 'active' AND (moderation_status = 'approved' OR moderation_status IS NULL)")
            products = cursor.fetchone()
            print(f"🛍️  Active Products: {products['count']}")
            
            # Check user searches
            cursor.execute("SELECT COUNT(*) as count FROM user_searches WHERE created_at >= DATE_SUB(NOW(), INTERVAL 90 DAY)")
            searches = cursor.fetchone()
            print(f"🔍 Recent Searches: {searches['count']}")
            
            # Check product views
            try:
                cursor.execute("SELECT COUNT(*) as count FROM product_views WHERE viewed_at >= DATE_SUB(NOW(), INTERVAL 90 DAY)")
                views = cursor.fetchone()
                print(f"👁️  Recent Views: {views['count']}")
            except:
                print("👁️  Recent Views: Table might not exist yet")
            
            cursor.close()
            conn.close()
            
            # Check if we have enough data
            if orders['count'] > 0 and products['count'] > 0:
                print(f"\n✅ Sufficient data for training!")
                return True
            else:
                print(f"\n⚠️  Insufficient data:")
                if orders['count'] == 0:
                    print("   - No orders found")
                if products['count'] == 0:
                    print("   - No active products found")
                return False
        else:
            print("❌ Connection failed")
            return False
    except Error as e:
        print(f"❌ Error: {e}")
        return False

# Try both configs
print("Checking database availability...")
print("\nThis script will test both production and local database configurations.")

success = False

# Try production first
if check_database(DB_CONFIG, "Production"):
    print("\n✅ Use production config in app.py")
    success = True
else:
    # Try local
    if check_database(DB_CONFIG_LOCAL, "Local XAMPP"):
        print("\n✅ Use local XAMPP config in app.py")
        success = True

if not success:
    print("\n" + "="*50)
    print("❌ No working database configuration found")
    print("\nPlease:")
    print("1. Make sure MySQL/XAMPP is running")
    print("2. Update DB_CONFIG in app.py with correct credentials")
    print("3. Make sure the database exists and has data")
    print("="*50)

