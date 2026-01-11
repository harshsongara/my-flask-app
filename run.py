#!/usr/bin/env python
"""
TimeTable Application Entry Point
Run this file to start the development server
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import create_app, db
from app.models import User, Task

# Create Flask application
app = create_app()


@app.shell_context_processor
def make_shell_context():
    """
    Make database models available in Flask shell.
    Usage: flask shell
    """
    return {
        'db': db,
        'User': User,
        'Task': Task
    }


@app.cli.command()
def init_db():
    """
    Initialize the database.
    Usage: flask init-db
    """
    db.create_all()
    print('Database initialized successfully!')


@app.cli.command()
def create_demo_user():
    """
    Create a demo user for testing.
    Usage: flask create-demo-user
    """
    # Check if demo user already exists
    demo_user = User.query.filter_by(username='demo').first()
    if demo_user:
        print('Demo user already exists!')
        return
    
    # Create demo user
    user = User(
        username='demo',
        email='demo@example.com',
        timezone='UTC'
    )
    user.set_password('demo123')
    
    db.session.add(user)
    db.session.commit()
    
    print('Demo user created successfully!')
    print('Username: demo')
    print('Password: demo123')


@app.cli.command()
def reset_db():
    """
    Reset the database (WARNING: Deletes all data).
    Usage: flask reset-db
    """
    response = input('This will delete all data. Are you sure? (yes/no): ')
    if response.lower() == 'yes':
        db.drop_all()
        db.create_all()
        print('Database reset successfully!')
    else:
        print('Operation cancelled.')


if __name__ == '__main__':
    # Run development server
    print("Starting TimeTable application...")
    print("Access the application at: http://localhost:5000")
    print("Press CTRL+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5000)
