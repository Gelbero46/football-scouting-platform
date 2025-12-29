from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import logging
import redis
from app.core.config import settings

# Import Base from models to ensure it's available
from app.models import Base

# PostgreSQL Engine
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,  # Disable connection pooling for development
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,  # Recycle connections every 5 minutes
    connect_args={
        "options": "-c timezone=utc"  # Set timezone to UTC
    }
)

# Configure root logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis connection with error handling
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    # Test Redis connection
    redis_client.ping()
    logger.info("✅ Redis connection successful")
except redis.RedisError as e:
    logger.error(f"❌ Redis connection failed: {e}")
    redis_client = None

# Database session dependency
def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Redis client dependency
def get_redis():
    """Dependency to get Redis client"""
    return redis_client

# Database utility functions
def test_connection():
    """Test database connectivity"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return result.fetchone()[0] == 1
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def get_db_info() -> dict:
    """Get database connection information for debugging"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT 
                    version() as version,
                    current_database() as database,
                    current_user as user,
                    inet_server_addr() as host,
                    inet_server_port() as port
            """))
            row = result.fetchone()
            return {
                "version": row[0],
                "database": row[1],
                "user": row[2],
                "host": row[3],
                "port": row[4],
                "url": settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else "hidden"
            }
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {"error": str(e)}

def health_check() -> dict:
    """Comprehensive health check for database and Redis"""
    health = {
        "database": {"status": "unhealthy", "details": {}},
        "redis": {"status": "unhealthy", "details": {}}
    }
    
    # Test database
    try:
        if test_connection():
            health["database"]["status"] = "healthy"
            health["database"]["details"] = get_db_info()
    except Exception as e:
        health["database"]["details"]["error"] = str(e)
    
    # Test Redis
    try:
        if redis_client:
            redis_client.ping()
            info = redis_client.info()
            health["redis"]["status"] = "healthy"
            health["redis"]["details"] = {
                "version": info.get("redis_version"),
                "memory_used": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients")
            }
    except Exception as e:
        health["redis"]["details"]["error"] = str(e)
    
    return health

def create_extensions():
    """Create required PostgreSQL extensions"""
    extensions = [
        'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";',
        'CREATE EXTENSION IF NOT EXISTS "pgcrypto";',
        'CREATE EXTENSION IF NOT EXISTS "pg_trgm";'
    ]
    
    try:
        with engine.connect() as connection:
            for ext in extensions:
                connection.execute(text(ext))
                connection.commit()
        print("✅ PostgreSQL extensions created successfully")
    except Exception as e:
        print(f"❌ Error creating extensions: {e}")

def reset_database():
    """Drop and recreate all tables (use with caution!)"""
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✅ Database reset successfully")
    except Exception as e:
        print(f"❌ Error resetting database: {e}")

# Initialize database connection on import
def init_db():
    """Initialize database connection and create extensions"""
    if test_connection():
        print("✅ Database connection successful")
        create_extensions()
    else:
        print("❌ Database connection failed")