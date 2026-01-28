"""
Migration script for gamification features
"""
import sqlite3
import os

# Get database path
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'timetable.db')

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

print(f"Connecting to database: {db_path}")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check existing columns in users table
cursor.execute("PRAGMA table_info(users)")
user_columns = [row[1] for row in cursor.fetchall()]

# User table migrations
user_migrations = []
if 'current_streak' not in user_columns:
    user_migrations.append("ALTER TABLE users ADD COLUMN current_streak INTEGER DEFAULT 0")
if 'longest_streak' not in user_columns:
    user_migrations.append("ALTER TABLE users ADD COLUMN longest_streak INTEGER DEFAULT 0")
if 'last_activity_date' not in user_columns:
    user_migrations.append("ALTER TABLE users ADD COLUMN last_activity_date DATE")
if 'daily_goal' not in user_columns:
    user_migrations.append("ALTER TABLE users ADD COLUMN daily_goal INTEGER DEFAULT 3")
if 'total_tasks_completed' not in user_columns:
    user_migrations.append("ALTER TABLE users ADD COLUMN total_tasks_completed INTEGER DEFAULT 0")
if 'streak_freeze_count' not in user_columns:
    user_migrations.append("ALTER TABLE users ADD COLUMN streak_freeze_count INTEGER DEFAULT 2")
if 'notification_enabled' not in user_columns:
    user_migrations.append("ALTER TABLE users ADD COLUMN notification_enabled BOOLEAN DEFAULT 1")
if 'reminder_time' not in user_columns:
    user_migrations.append("ALTER TABLE users ADD COLUMN reminder_time TIME DEFAULT '18:00:00'")

# Create achievements table
cursor.execute("""
CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255) NOT NULL,
    icon VARCHAR(10) DEFAULT '🏆',
    category VARCHAR(50) DEFAULT 'general',
    requirement_type VARCHAR(50) NOT NULL,
    requirement_value INTEGER NOT NULL,
    points INTEGER DEFAULT 10
)
""")

# Create user_achievements table
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    achievement_id INTEGER NOT NULL,
    earned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (achievement_id) REFERENCES achievements (id),
    UNIQUE(user_id, achievement_id)
)
""")

print(f"Running {len(user_migrations)} user table migrations...")
for sql in user_migrations:
    print(f"  - {sql}")
    cursor.execute(sql)

# Insert default achievements
achievements_data = [
    ('Getting Started', 'Complete your first task', '🎯', 'milestone', 'total_tasks', 1, 5),
    ('Day 1', 'Start your first streak', '🔥', 'streak', 'streak', 1, 10),
    ('Hot Streak', '3 days in a row!', '🔥', 'streak', 'streak', 3, 25),
    ('On Fire', '7 days in a row!', '🚀', 'streak', 'streak', 7, 50),
    ('Unstoppable', '30 days in a row!', '⚡', 'streak', 'streak', 30, 200),
    ('Legend', '100 days in a row!', '👑', 'streak', 'streak', 100, 500),
    ('Productive', 'Complete 10 tasks', '📋', 'milestone', 'total_tasks', 10, 20),
    ('Task Master', 'Complete 50 tasks', '🏆', 'milestone', 'total_tasks', 50, 100),
    ('Achiever', 'Complete 100 tasks', '🎖️', 'milestone', 'total_tasks', 100, 250),
    ('Champion', 'Complete 500 tasks', '🥇', 'milestone', 'total_tasks', 500, 1000),
    ('Goal Crusher', 'Reach your daily goal', '🎯', 'daily', 'daily_goal', 3, 15),
    ('Overachiever', 'Complete 5 tasks in one day', '⭐', 'daily', 'daily_goal', 5, 30),
    ('Productivity Beast', 'Complete 10 tasks in one day', '🦾', 'daily', 'daily_goal', 10, 50)
]

for ach in achievements_data:
    cursor.execute("""
        INSERT OR IGNORE INTO achievements 
        (name, description, icon, category, requirement_type, requirement_value, points)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ach)

conn.commit()
print("✅ Gamification migration completed successfully!")

# Update existing users' total_tasks_completed
cursor.execute("""
    UPDATE users SET total_tasks_completed = (
        SELECT COUNT(*) FROM tasks 
        WHERE tasks.user_id = users.id AND tasks.completed_at IS NOT NULL
    ) WHERE total_tasks_completed = 0
""")

conn.commit()
print("✅ Updated existing users' task counts!")

conn.close()