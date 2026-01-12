"""
WSGI Application Entry Point for Production Deployment
This file is used by WSGI servers like Gunicorn
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the Flask app
from app import create_app
from app.models import db

# Create the application instance
app = create_app()

# Auto-initialize database tables on startup (for Render deployment)
with app.app_context():
    try:
        db.create_all()
        print("Database tables initialized successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise

if __name__ == '__main__':
    # This is only used when running directly (not recommended for production)
    # Use gunicorn or another WSGI server instead
    app.run()
