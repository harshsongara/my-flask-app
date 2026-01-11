from datetime import datetime, timedelta
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import pytz


class User(UserMixin, db.Model):
    """User account model."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    timezone = db.Column(db.String(50), default='UTC')
    
    # Relationships
    tasks = db.relationship('Task', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_timezone(self):
        """Get user's timezone object."""
        return pytz.timezone(self.timezone)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Task(db.Model):
    """Task model with flexible completion windows."""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    window_type = db.Column(db.String(20), nullable=False)  # 'daily', 'weekly', 'monthly', 'custom'
    window_value = db.Column(db.Integer)  # Days for custom windows
    deadline = db.Column(db.DateTime, nullable=False, index=True)
    completed_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active', index=True)  # 'active', 'completed', 'overdue', 'archived'
    priority = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high'
    tags = db.Column(db.String(500))  # Comma-separated tags
    completion_quality = db.Column(db.String(20))  # 'on_time', 'late'
    
    def is_completed(self):
        """Check if task is completed."""
        return self.completed_at is not None
    
    def is_overdue(self):
        """Check if task is overdue."""
        if self.is_completed():
            return False
        return datetime.utcnow() > self.deadline
    
    def is_at_risk(self):
        """Check if task is at risk (less than 20% time remaining)."""
        if self.is_completed() or self.is_overdue():
            return False
        
        total_time = (self.deadline - self.created_at).total_seconds()
        remaining_time = (self.deadline - datetime.utcnow()).total_seconds()
        
        return (remaining_time / total_time) < 0.2
    
    def time_remaining(self):
        """Get human-readable time remaining."""
        if self.is_completed():
            return "Completed"
        
        if self.is_overdue():
            delta = datetime.utcnow() - self.deadline
            return f"Overdue by {self._format_timedelta(delta)}"
        
        delta = self.deadline - datetime.utcnow()
        return f"{self._format_timedelta(delta)} remaining"
    
    def _format_timedelta(self, delta):
        """Format timedelta to human-readable string."""
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def get_tags_list(self):
        """Get tags as a list."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def __repr__(self):
        return f'<Task {self.title}>'
