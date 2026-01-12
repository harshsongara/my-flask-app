import os
from datetime import timedelta

# Get the absolute path to the project root directory
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration."""
    # IMPORTANT: Change this secret key in production!
    # Generate a secure key with: python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'CHANGE-THIS-SECRET-KEY-IN-PRODUCTION'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Build database path - ensure absolute path with forward slashes for SQLite URI
    _db_path = os.path.join(basedir, 'instance', 'timetable.db')
    
    # Convert to forward slashes for SQLite URI (works on both Windows and Unix)
    _db_path = _db_path.replace('\\', '/')
    
    # SQLite URI format: sqlite:///absolute/path/to/db.db
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{_db_path}'
    
    # SQLAlchemy engine options - works with both SQLite and PostgreSQL
    # Only set pool_pre_ping (works for both), skip SQLite-specific options
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
    }
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_SECURE = False  # Set True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Default timezone
    DEFAULT_TIMEZONE = os.environ.get('DEFAULT_TIMEZONE', 'UTC')
    
    # Pagination
    TASKS_PER_PAGE = 50


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    
    # SQLite-specific engine options for local development
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'check_same_thread': False,
            'timeout': 30
        },
        'pool_pre_ping': True,
    }


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # Require HTTPS


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
