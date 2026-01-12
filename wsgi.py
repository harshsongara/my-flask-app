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
        
        # Add missing columns for recurring tasks (PostgreSQL migration)
        from sqlalchemy import text, inspect
        inspector = inspect(db.engine)
        
        # Check if tasks table exists
        if 'tasks' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('tasks')]
            
            migrations = []
            if 'is_recurring' not in columns:
                migrations.append("ALTER TABLE tasks ADD COLUMN is_recurring BOOLEAN DEFAULT false")
            if 'recurrence_pattern' not in columns:
                migrations.append("ALTER TABLE tasks ADD COLUMN recurrence_pattern VARCHAR(20)")
            if 'recurrence_interval' not in columns:
                migrations.append("ALTER TABLE tasks ADD COLUMN recurrence_interval INTEGER DEFAULT 1")
            if 'parent_task_id' not in columns:
                migrations.append("ALTER TABLE tasks ADD COLUMN parent_task_id INTEGER")
            
            if migrations:
                print(f"Running {len(migrations)} column migrations...")
                for sql in migrations:
                    print(f"  - {sql}")
                    db.session.execute(text(sql))
                db.session.commit()
                print("✅ Column migrations completed!")
            else:
                print("✅ All columns already exist")
                
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise

if __name__ == '__main__':
    # This is only used when running directly (not recommended for production)
    # Use gunicorn or another WSGI server instead
    app.run()
