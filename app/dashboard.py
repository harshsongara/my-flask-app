from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Task
from app.utils import (
    refresh_user_task_statuses,
    get_daily_stats,
    get_weekly_stats,
    get_monthly_stats,
    get_weekly_trend
)
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def home():
    """Main dashboard with overview statistics."""
    # Refresh task statuses
    refresh_user_task_statuses(db.session, current_user.id)
    
    # Update user streak (check daily)
    current_user.update_streak(task_completed_today=False)  # Will be updated to True when tasks completed
    
    # Get statistics
    today_stats = get_daily_stats(db.session, current_user.id)
    week_stats = get_weekly_stats(db.session, current_user.id)
    month_stats = get_monthly_stats(db.session, current_user.id)
    
    # Get gamification data
    progress = current_user.get_today_progress()
    recent_achievements = current_user.achievements.order_by(
        db.desc('earned_at')
    ).limit(3).all()
    
    # Get task counts by status
    active_count = Task.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).count()
    
    at_risk_count = Task.query.filter_by(
        user_id=current_user.id,
        status='at_risk'
    ).count()
    
    overdue_count = Task.query.filter_by(
        user_id=current_user.id,
        status='overdue'
    ).count()
    
    # Get upcoming tasks (next 5 due)
    upcoming_tasks = Task.query.filter_by(
        user_id=current_user.id
    ).filter(
        Task.status.in_(['active', 'at_risk'])
    ).order_by(Task.deadline.asc()).limit(5).all()
    
    # Get recent completions (last 5)
    recent_completed = Task.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).order_by(Task.completed_at.desc()).limit(5).all()
    
    return render_template('dashboard/home.html',
                         today_stats=today_stats,
                         week_stats=week_stats,
                         month_stats=month_stats,
                         active_count=active_count,
                         at_risk_count=at_risk_count,
                         overdue_count=overdue_count,
                         upcoming_tasks=upcoming_tasks,
                         recent_completed=recent_completed,
                         # Gamification data
                         streak=current_user.current_streak,
                         longest_streak=current_user.longest_streak,
                         progress=progress,
                         recent_achievements=recent_achievements,
                         total_tasks=current_user.total_tasks_completed,
                         streak_freeze_count=current_user.streak_freeze_count)


@dashboard_bp.route('/daily')
@login_required
def daily():
    """Daily progress view."""
    refresh_user_task_statuses(db.session, current_user.id)
    
    # Get today's tasks
    today = datetime.utcnow().date()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())
    
    tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.deadline >= start,
        Task.deadline <= end,
        Task.status != 'archived'
    ).order_by(Task.priority.desc(), Task.deadline.asc()).all()
    
    stats = get_daily_stats(db.session, current_user.id)
    
    return render_template('dashboard/daily.html', tasks=tasks, stats=stats, date=today)


@dashboard_bp.route('/weekly')
@login_required
def weekly():
    """Weekly progress view."""
    refresh_user_task_statuses(db.session, current_user.id)
    
    # Get this week's tasks
    start_date = datetime.utcnow().date() - timedelta(days=6)
    end_date = datetime.utcnow().date()
    
    start = datetime.combine(start_date, datetime.min.time())
    end = datetime.combine(end_date, datetime.max.time())
    
    tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.deadline >= start,
        Task.deadline <= end,
        Task.status != 'archived'
    ).order_by(Task.deadline.asc()).all()
    
    stats = get_weekly_stats(db.session, current_user.id, start_date)
    trend_data = get_weekly_trend(db.session, current_user.id, days=7)
    
    return render_template('dashboard/weekly.html',
                         tasks=tasks,
                         stats=stats,
                         trend_data=trend_data,
                         start_date=start_date,
                         end_date=end_date)


@dashboard_bp.route('/monthly')
@login_required
def monthly():
    """Monthly progress view."""
    refresh_user_task_statuses(db.session, current_user.id)
    
    # Get this month's tasks
    now = datetime.utcnow()
    start = datetime(now.year, now.month, 1)
    
    if now.month == 12:
        end = datetime(now.year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end = datetime(now.year, now.month + 1, 1) - timedelta(seconds=1)
    
    tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.deadline >= start,
        Task.deadline <= end,
        Task.status != 'archived'
    ).order_by(Task.deadline.asc()).all()
    
    stats = get_monthly_stats(db.session, current_user.id, now.year, now.month)
    trend_data = get_weekly_trend(db.session, current_user.id, days=30)
    
    return render_template('dashboard/monthly.html',
                         tasks=tasks,
                         stats=stats,
                         trend_data=trend_data,
                         month=now.strftime('%B %Y'))


@dashboard_bp.route('/api/trend-data')
@login_required
def api_trend_data():
    """API endpoint for chart data."""
    days = int(request.args.get('days', 7))
    trend_data = get_weekly_trend(db.session, current_user.id, days=days)
    
    return jsonify({
        'labels': [d['date'] for d in trend_data],
        'created': [d['created'] for d in trend_data],
        'completed': [d['completed'] for d in trend_data]
    })
