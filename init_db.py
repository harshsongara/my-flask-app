"""Simple initialization script to set up the database"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from app import db, create_app

# Create app
print("Creating Flask application...")
app = create_app()

print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Create database
print("Initializing database...")
with app.app_context():
    db.create_all()
    print("✓ Database created successfully!")
    print(f"✓ Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")

print("\nYou can now run the application with: python run.py")
