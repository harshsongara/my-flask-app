from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from app import db
from app.models import Task
from app.utils import calculate_deadline, update_task_status, refresh_user_task_statuses
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')


class TaskForm(FlaskForm):
    """Task creation/editing form."""
    title = StringField('Task Title', validators=[
        DataRequired(),
        Length(min=1, max=200, message='Title must be between 1 and 200 characters')
    ])
    description = TextAreaField('Description', validators=[Optional()])
    window_type = SelectField('Completion Window', 
        choices=[
            ('daily', 'Daily (by end of day)'),
            ('weekly', 'Weekly (7 days)'),
            ('monthly', 'Monthly (30 days)'),
            ('custom', 'Custom (specify days)')
        ],
        validators=[DataRequired()]
    )
    window_value = IntegerField('Custom Days', validators=[
        Optional(),
        NumberRange(min=1, max=365, message='Must be between 1 and 365 days')
    ])
    priority = SelectField('Priority',
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High')
        ],
        default='medium'
    )
    tags = StringField('Tags (comma-separated)', validators=[Optional()])
    submit = SubmitField('Create Task')


@tasks_bp.route('/')
@login_required
def list_tasks():
    """List all active tasks for current user."""
    # Refresh task statuses
    refresh_user_task_statuses(db.session, current_user.id)
    
    # Get filter from query params
    status_filter = request.args.get('status', 'active')
    
    # Query tasks
    query = Task.query.filter_by(user_id=current_user.id)
    
    if status_filter == 'active':
        query = query.filter(Task.status.in_(['active', 'at_risk']))
    elif status_filter == 'overdue':
        query = query.filter_by(status='overdue')
    elif status_filter == 'completed':
        query = query.filter_by(status='completed')
    elif status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    # Order by deadline (upcoming first)
    tasks = query.order_by(Task.deadline.asc()).all()
    
    return render_template('tasks/list.html', tasks=tasks, status_filter=status_filter)


@tasks_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new task."""
    form = TaskForm()
    
    if form.validate_on_submit():
        # Calculate deadline
        deadline = calculate_deadline(
            datetime.utcnow(),
            form.window_type.data,
            form.window_value.data,
            current_user.timezone
        )
        
        # Create task
        task = Task(
            user_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            window_type=form.window_type.data,
            window_value=form.window_value.data if form.window_type.data == 'custom' else None,
            deadline=deadline,
            priority=form.priority.data,
            tags=form.tags.data,
            status='active'
        )
        
        db.session.add(task)
        db.session.commit()
        
        flash(f'Task "{task.title}" created successfully!', 'success')
        return redirect(url_for('tasks.list_tasks'))
    
    return render_template('tasks/create.html', form=form)


@tasks_bp.route('/<int:task_id>')
@login_required
def detail(task_id):
    """View task details."""
    task = Task.query.get_or_404(task_id)
    
    # Security: Verify ownership
    if task.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('tasks.list_tasks'))
    
    # Update status
    update_task_status(task)
    db.session.commit()
    
    return render_template('tasks/detail.html', task=task)


@tasks_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(task_id):
    """Edit an existing task."""
    task = Task.query.get_or_404(task_id)
    
    # Security: Verify ownership
    if task.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('tasks.list_tasks'))
    
    form = TaskForm(obj=task)
    form.submit.label.text = 'Update Task'
    
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.priority = form.priority.data
        task.tags = form.tags.data
        
        # Recalculate deadline if window changed
        if form.window_type.data != task.window_type or \
           (form.window_type.data == 'custom' and form.window_value.data != task.window_value):
            task.window_type = form.window_type.data
            task.window_value = form.window_value.data if form.window_type.data == 'custom' else None
            task.deadline = calculate_deadline(
                task.created_at,
                task.window_type,
                task.window_value,
                current_user.timezone
            )
        
        db.session.commit()
        flash(f'Task "{task.title}" updated successfully!', 'success')
        return redirect(url_for('tasks.detail', task_id=task.id))
    
    return render_template('tasks/edit.html', form=form, task=task)


@tasks_bp.route('/<int:task_id>/complete', methods=['POST'])
@login_required
def complete(task_id):
    """Mark a task as completed."""
    task = Task.query.get_or_404(task_id)
    
    # Security: Verify ownership
    if task.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    if task.is_completed():
        return jsonify({'success': False, 'error': 'Task already completed'}), 400
    
    # Mark completed
    task.completed_at = datetime.utcnow()
    task.status = 'completed'
    
    # Determine completion quality
    if task.completed_at <= task.deadline:
        task.completion_quality = 'on_time'
    else:
        task.completion_quality = 'late'
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Task "{task.title}" completed!',
        'completion_quality': task.completion_quality
    })


@tasks_bp.route('/<int:task_id>/uncomplete', methods=['POST'])
@login_required
def uncomplete(task_id):
    """Mark a completed task as active again."""
    task = Task.query.get_or_404(task_id)
    
    # Security: Verify ownership
    if task.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    if not task.is_completed():
        return jsonify({'success': False, 'error': 'Task not completed'}), 400
    
    # Mark as active
    task.completed_at = None
    task.completion_quality = None
    update_task_status(task)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Task "{task.title}" marked as active'
    })


@tasks_bp.route('/<int:task_id>/delete', methods=['POST'])
@login_required
def delete(task_id):
    """Delete (archive) a task."""
    task = Task.query.get_or_404(task_id)
    
    # Security: Verify ownership
    if task.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('tasks.list_tasks'))
    
    # Soft delete (archive)
    task.status = 'archived'
    db.session.commit()
    
    flash(f'Task "{task.title}" archived.', 'info')
    return redirect(url_for('tasks.list_tasks'))
