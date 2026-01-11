from datetime import datetime, timedelta, time
from app.models import Task
from sqlalchemy import func
import pytz


def calculate_deadline(created_at, window_type, custom_days=None, timezone='UTC'):
    """
    Calculate task deadline based on window type.
    
    Args:
        created_at: DateTime when task was created
        window_type: 'daily', 'weekly', 'monthly', or 'custom'
        custom_days: Number of days for custom windows
        timezone: User's timezone string
    
    Returns:
        DateTime of the deadline
    """
    tz = pytz.timezone(timezone)
    
    if window_type == 'daily':
        # End of the same day in user's timezone
        local_created = created_at.replace(tzinfo=pytz.UTC).astimezone(tz)
        deadline_local = datetime.combine(local_created.date(), time(23, 59, 59))
        deadline = tz.localize(deadline_local).astimezone(pytz.UTC).replace(tzinfo=None)
    elif window_type == 'weekly':
        deadline = created_at + timedelta(days=7)
    elif window_type == 'monthly':
        deadline = created_at + timedelta(days=30)
    elif window_type == 'custom' and custom_days:
        deadline = created_at + timedelta(days=custom_days)
    else:
        # Default to 1 day if invalid
        deadline = created_at + timedelta(days=1)
    
    return deadline


def update_task_status(task):
    """
    Update task status based on current time.
    
    Args:
        task: Task object to update
    
    Returns:
        Updated status string
    """
    if task.completed_at:
        return 'completed'
    
    if datetime.utcnow() > task.deadline:
        task.status = 'overdue'
    elif task.is_at_risk():
        task.status = 'at_risk'
    else:
        task.status = 'active'
    
    return task.status


def refresh_user_task_statuses(db_session, user_id):
    """
    Update statuses for all non-completed tasks for a user.
    
    Args:
        db_session: SQLAlchemy database session
        user_id: User ID to update tasks for
    """
    active_tasks = Task.query.filter_by(
        user_id=user_id,
        completed_at=None
    ).all()
    
    for task in active_tasks:
        update_task_status(task)
    
    db_session.commit()


def get_completion_rate(db_session, user_id, period_start, period_end):
    """
    Calculate task completion rate for a date range.
    
    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
        period_start: Start datetime
        period_end: End datetime
    
    Returns:
        Dictionary with completion statistics
    """
    # Tasks with deadline in the period
    tasks = Task.query.filter(
        Task.user_id == user_id,
        Task.deadline >= period_start,
        Task.deadline <= period_end,
        Task.status != 'archived'
    ).all()
    
    total = len(tasks)
    if total == 0:
        return {
            'total': 0,
            'completed': 0,
            'on_time': 0,
            'late': 0,
            'overdue': 0,
            'completion_rate': 0,
            'on_time_rate': 0
        }
    
    completed = sum(1 for t in tasks if t.is_completed())
    on_time = sum(1 for t in tasks if t.completion_quality == 'on_time')
    late = sum(1 for t in tasks if t.completion_quality == 'late')
    overdue = sum(1 for t in tasks if t.is_overdue())
    
    completion_rate = (completed / total * 100) if total > 0 else 0
    on_time_rate = (on_time / total * 100) if total > 0 else 0
    
    return {
        'total': total,
        'completed': completed,
        'on_time': on_time,
        'late': late,
        'overdue': overdue,
        'completion_rate': round(completion_rate, 1),
        'on_time_rate': round(on_time_rate, 1)
    }


def get_daily_stats(db_session, user_id, date=None):
    """Get statistics for a specific day."""
    if date is None:
        date = datetime.utcnow().date()
    
    start = datetime.combine(date, time.min)
    end = datetime.combine(date, time.max)
    
    return get_completion_rate(db_session, user_id, start, end)


def get_weekly_stats(db_session, user_id, start_date=None):
    """Get statistics for a 7-day period."""
    if start_date is None:
        start_date = datetime.utcnow().date() - timedelta(days=6)
    
    start = datetime.combine(start_date, time.min)
    end = datetime.combine(start_date + timedelta(days=6), time.max)
    
    return get_completion_rate(db_session, user_id, start, end)


def get_monthly_stats(db_session, user_id, year=None, month=None):
    """Get statistics for a calendar month."""
    if year is None or month is None:
        now = datetime.utcnow()
        year = now.year
        month = now.month
    
    start = datetime(year, month, 1)
    
    # Calculate last day of month
    if month == 12:
        end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end = datetime(year, month + 1, 1) - timedelta(seconds=1)
    
    return get_completion_rate(db_session, user_id, start, end)


def get_weekly_trend(db_session, user_id, days=7):
    """
    Get daily completion data for the last N days.
    
    Returns:
        List of dictionaries with date, created, completed counts
    """
    trend_data = []
    end_date = datetime.utcnow().date()
    
    for i in range(days - 1, -1, -1):
        date = end_date - timedelta(days=i)
        start = datetime.combine(date, time.min)
        end = datetime.combine(date, time.max)
        
        created = Task.query.filter(
            Task.user_id == user_id,
            Task.created_at >= start,
            Task.created_at <= end
        ).count()
        
        completed = Task.query.filter(
            Task.user_id == user_id,
            Task.completed_at >= start,
            Task.completed_at <= end
        ).count()
        
        trend_data.append({
            'date': date.strftime('%a'),  # Mon, Tue, etc.
            'created': created,
            'completed': completed
        })
    
    return trend_data
