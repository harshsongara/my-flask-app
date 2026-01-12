from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
import os

db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_name=None):
    """Application factory pattern."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Get the parent directory (project root) for templates and static files
    import sys
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    instance_path = os.path.join(parent_dir, 'instance')
    
    app = Flask(__name__, 
                instance_relative_config=False,
                instance_path=instance_path,
                template_folder=os.path.join(parent_dir, 'templates'),
                static_folder=os.path.join(parent_dir, 'static'))
    app.config.from_object(config[config_name])
    
    # Ensure instance folder exists
    os.makedirs(instance_path, exist_ok=True)
    
    # Log database path for debugging
    print(f"Config name: {config_name}")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Engine options: {app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {})}")
    print(f"Instance path: {instance_path}")
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Create tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created/verified successfully")
        except Exception as e:
            print(f"Error creating database tables: {e}")
    
    # Register blueprints
    from app.auth import auth_bp
    from app.tasks import tasks_bp
    from app.dashboard import dashboard_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(dashboard_bp)
    
    return app
