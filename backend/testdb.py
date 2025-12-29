import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings

db_url = settings.DATABASE_URL

try:
    conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print(f"Connected to: {db_url}")

    # Check PostgreSQL version
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✅ Connected successfully! PostgreSQL version: {version['version']}")

    # Try to fetch users
    cursor.execute("SELECT id, email, role, created_at FROM users LIMIT 10;")
    users = cursor.fetchall()

    if users:
        print("\n👥 Users in database:")
        for u in users:
            print(f"- ID: {u['id']} | Email: {u['email']} | Role: {u['role']} | Created At: {u['created_at']}")
    else:
        print("\n⚠️ No users found in the 'users' table.")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Connection failed: {e}")
