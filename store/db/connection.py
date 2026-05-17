import os
import mysql.connector
from mysql.connector import pooling

# НЕ створюємо pool при імпорті
_connection_pool = None


def create_connection_pool():
    """Create database connection pool with Cloud Run support"""
    db_host = os.environ.get("DB_HOST", "localhost")
    
    # Check if using Cloud SQL unix socket
    if db_host.startswith("/cloudsql/"):
        connection_config = {
            "unix_socket": db_host,
            "user": os.environ.get("DB_USER", "myuser"),
            "password": os.environ.get("DB_PASSWORD", "mypassword"),
            "database": os.environ.get("DB_NAME", "mydb"),
            "pool_name": "mypool",
            "pool_size": 5,
            "pool_reset_session": True,
        }
    else:
        connection_config = {
            "host": db_host,
            "user": os.environ.get("DB_USER", "myuser"),
            "password": os.environ.get("DB_PASSWORD", "mypassword"),
            "database": os.environ.get("DB_NAME", "mydb"),
            "port": int(os.environ.get("DB_PORT", 3306)),
            "pool_name": "mypool",
            "pool_size": 5,
            "pool_reset_session": True,
        }
    
    try:
        pool = pooling.MySQLConnectionPool(**connection_config)
        print(f"✓ Database connection pool created for {db_host}")
        return pool
    except Exception as e:
        print(f"✗ Error creating connection pool: {e}")
        # Не викидаємо помилку - дозволяємо додатку запуститися
        return None


def get_db_connection():
    """Get connection from pool with lazy initialization and automatic retry"""
    global _connection_pool
    
    if _connection_pool is None:
        _connection_pool = create_connection_pool()
    
    if _connection_pool is None:
        raise Exception("Database connection pool is not available")
    
    try:
        return _connection_pool.get_connection()
    except mysql.connector.Error as err:
        print(f"Error getting connection from pool: {err}")
        # Try to recreate pool if it's broken
        _connection_pool = create_connection_pool()
        if _connection_pool is None:
            raise Exception("Failed to recreate connection pool")
        return _connection_pool.get_connection()


db_connection = None
