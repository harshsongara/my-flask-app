# TimeTable - Flexible Task Management System

A Python-based web application for managing tasks with flexible completion windows instead of rigid time slots.

## Features

- **Flexible Task Windows**: Tasks use completion windows (daily, weekly, monthly, or custom) instead of specific time slots
- **User Authentication**: Secure user accounts with session management
- **Progress Tracking**: Visual dashboards showing daily, weekly, and monthly progress
- **Automatic Status Updates**: Tasks automatically marked as active, at-risk, overdue, or completed
- **Clean UI**: Traditional, readable interface with modern styling
- **Persistent Data**: All progress saved across sessions

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download this project**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Update `SECRET_KEY` with a random string (important for production)

6. **Initialize the database**:
   ```bash
   python run.py
   ```
   Or use Flask CLI:
   ```bash
   flask init-db
   ```

7. **Create a demo user** (optional):
   ```bash
   flask create-demo-user
   ```
   This creates a user with:
   - Username: `demo`
   - Password: `demo123`

8. **Run the application**:
   ```bash
   python run.py
   ```

9. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

### Creating Tasks

1. Click "New Task" button
2. Enter task details:
   - **Title**: What needs to be done
   - **Description**: Optional details
   - **Completion Window**: Daily, Weekly, Monthly, or Custom
   - **Priority**: Low, Medium, or High
   - **Tags**: Optional comma-separated tags

3. Tasks automatically calculate deadlines based on the window type

### Viewing Progress

- **Dashboard**: Overview of today, this week, and this month
- **Daily View**: Tasks due today with completion stats
- **Weekly View**: 7-day overview with trend chart
- **Monthly View**: Month-long view with activity graph

### Task Management

- **Mark Complete**: Click the checkmark (✓) button
- **Reopen Task**: Click the return (↩) button on completed tasks
- **Edit Task**: Click the pencil icon or view task details
- **Archive Task**: Remove from active view (preserves data)

## Project Structure

```
timetable/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models (User, Task)
│   ├── auth.py              # Authentication routes
│   ├── tasks.py             # Task management routes
│   ├── dashboard.py         # Analytics and progress views
│   └── utils.py             # Helper functions
├── static/
│   ├── css/                 # Stylesheets
│   └── js/                  # JavaScript files
├── templates/               # Jinja2 HTML templates
├── instance/                # Database and instance-specific files
├── config.py                # Configuration classes
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Flask CLI Commands

```bash
# Initialize database
flask init-db

# Create demo user
flask create-demo-user

# Reset database (WARNING: deletes all data)
flask reset-db

# Open interactive shell with database context
flask shell
```

## Configuration

Edit `config.py` or set environment variables in `.env`:

- `SECRET_KEY`: Secret key for session encryption (required)
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `DEFAULT_TIMEZONE`: Default timezone for new users (defaults to UTC)

## Development

### Running Tests

```bash
pytest
```

### Database Migrations

For production deployment, use Alembic for database migrations:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Deployment

### Production Checklist

1. Set `FLASK_ENV=production` in environment
2. Generate a strong `SECRET_KEY`
3. Use PostgreSQL instead of SQLite
4. Enable HTTPS and set `SESSION_COOKIE_SECURE=True`
5. Use a production WSGI server (Gunicorn, uWSGI)
6. Set up reverse proxy (Nginx, Apache)

### Example with Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "run:app"
```

## Architecture Highlights

- **Flask**: Lightweight web framework
- **SQLAlchemy**: Database ORM with support for SQLite/PostgreSQL
- **Flask-Login**: Session-based authentication
- **Jinja2**: Server-side templating
- **Chart.js**: Client-side data visualization

## Philosophy

TimeTable embraces **flexible completion windows** over rigid scheduling:

- No forced time slots or hourly planning
- Tasks defined by completion timeframes (days/weeks/months)
- Focus on progress trends rather than militant adherence
- Works with how people actually complete tasks

## License

This project is provided as-is for educational and personal use.

## Support

For issues or questions, refer to the system design document: `SYSTEM_DESIGN.md`

---

**Built with ❤️ for flexible productivity**
