"""Test database connection"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from config import Config

print("=" * 60)
print("Database Configuration Test")
print("=" * 60)
print(f"Base directory: {os.path.abspath(os.path.dirname(__file__))}")
print(f"Database URI: {Config.SQLALCHEMY_DATABASE_URI}")

# Extract actual file path from URI
db_uri = Config.SQLALCHEMY_DATABASE_URI
if db_uri.startswith('sqlite:///'):
    db_path = db_uri.replace('sqlite:///', '')
    # Convert forward slashes back to backslashes for Windows
    db_path_win = db_path.replace('/', '\\')
    
    print(f"Database file path (URI): {db_path}")
    print(f"Database file path (Win): {db_path_win}")
    print(f"File exists: {os.path.exists(db_path_win)}")
    print(f"File size: {os.path.getsize(db_path_win) if os.path.exists(db_path_win) else 'N/A'} bytes")
    print(f"Directory exists: {os.path.exists(os.path.dirname(db_path_win))}")
    
    # Test SQLite connection directly
    try:
        import sqlite3
        conn = sqlite3.connect(db_path_win)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables in database: {[t[0] for t in tables]}")
        conn.close()
        print("✓ Direct SQLite connection successful!")
    except Exception as e:
        print(f"✗ Direct SQLite connection failed: {e}")
    
    # Test with SQLAlchemy
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, 
                              connect_args={'check_same_thread': False})
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ SQLAlchemy connection successful!")
    except Exception as e:
        print(f"✗ SQLAlchemy connection failed: {e}")

print("=" * 60)
