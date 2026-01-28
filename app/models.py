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
    
    # Gamification fields
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date)
    daily_goal = db.Column(db.Integer, default=3)  # Default: 3 tasks per day
    total_tasks_completed = db.Column(db.Integer, default=0)
    streak_freeze_count = db.Column(db.Integer, default=2)  # Streak protection uses
    notification_enabled = db.Column(db.Boolean, default=True)
    reminder_time = db.Column(db.Time, default=lambda: datetime.strptime('18:00', '%H:%M').time())
    
    # Relationships
    tasks = db.relationship('Task', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    achievements = db.relationship('UserAchievement', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_timezone(self):
        """Get user's timezone object."""
        return pytz.timezone(self.timezone)
    
    def update_streak(self, task_completed_today=True):
        """Update user's daily streak based on task completion."""
        today = datetime.utcnow().date()
        
        if self.last_activity_date == today:
            return  # Already updated today
        
        yesterday = today - timedelta(days=1)
        
        if task_completed_today:
            # User completed task(s) today
            if self.last_activity_date == yesterday:
                # Continuing streak
                self.current_streak += 1
            else:
                # Starting new streak
                self.current_streak = 1
            
            self.last_activity_date = today
            
            # Update longest streak
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        else:
            # No tasks completed - check if streak should be broken
            if self.last_activity_date and self.last_activity_date < yesterday:
                # More than 1 day gap - break streak unless using streak freeze
                if self.streak_freeze_count > 0:
                    self.streak_freeze_count -= 1
                    # Don't break streak, but don't extend either
                else:
                    self.current_streak = 0
    
    def get_today_progress(self):
        """Get today's task completion progress."""
        today = datetime.utcnow().date()
        start = datetime.combine(today, datetime.min.time())
        end = datetime.combine(today, datetime.max.time())
        
        completed_today = self.tasks.filter(
            Task.completed_at >= start,
            Task.completed_at <= end
        ).count()
        
        return {
            'completed': completed_today,
            'goal': self.daily_goal,
            'percentage': min(100, (completed_today / self.daily_goal) * 100) if self.daily_goal > 0 else 0
        }
    
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
    
    # Recurring task fields
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_pattern = db.Column(db.String(20))  # 'daily', 'weekly', 'monthly', 'custom'
    recurrence_interval = db.Column(db.Integer, default=1)  # Every X days/weeks/months
    parent_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))  # For tracking recurring instances
    
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
    
    def create_next_recurrence(self):
        """Create the next recurring instance when this task is completed."""
        if not self.is_recurring:
            return None
        
        # Calculate next deadline based on pattern
        if self.recurrence_pattern == 'daily':
            next_deadline = self.deadline + timedelta(days=self.recurrence_interval)
        elif self.recurrence_pattern == 'weekly':
            next_deadline = self.deadline + timedelta(weeks=self.recurrence_interval)
        elif self.recurrence_pattern == 'monthly':
            # Approximate month as 30 days
            next_deadline = self.deadline + timedelta(days=30 * self.recurrence_interval)
        else:
            return None
        
        # Create new task instance
        new_task = Task(
            user_id=self.user_id,
            title=self.title,
            description=self.description,
            window_type=self.window_type,
            window_value=self.window_value,
            deadline=next_deadline,
            priority=self.priority,
            tags=self.tags,
            is_recurring=True,
            recurrence_pattern=self.recurrence_pattern,
            recurrence_interval=self.recurrence_interval,
            parent_task_id=self.parent_task_id or self.id
        )
        
        return new_task
    
    def __repr__(self):
        return f'<Task {self.title}>'


class Achievement(db.Model):
    """Achievement/Badge definitions."""
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(10), default='🏆')  # Emoji icon
    category = db.Column(db.String(50), default='general')  # streak, completion, milestone
    requirement_type = db.Column(db.String(50), nullable=False)  # streak, tasks_completed, etc.
    requirement_value = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, default=10)
    
    def __repr__(self):
        return f'<Achievement {self.name}>'


class UserAchievement(db.Model):
    """User's earned achievements."""
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    achievement = db.relationship('Achievement', backref='user_achievements')
    
    def __repr__(self):
        return f'<UserAchievement {self.user_id}:{self.achievement_id}>'
