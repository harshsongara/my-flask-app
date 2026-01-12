"""
Migration script to add recurring task columns
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

# Check if columns already exist
cursor.execute("PRAGMA table_info(tasks)")
columns = [row[1] for row in cursor.fetchall()]

migrations = []

if 'is_recurring' not in columns:
    migrations.append("ALTER TABLE tasks ADD COLUMN is_recurring BOOLEAN DEFAULT 0")
    
if 'recurrence_pattern' not in columns:
    migrations.append("ALTER TABLE tasks ADD COLUMN recurrence_pattern VARCHAR(20)")
    
if 'recurrence_interval' not in columns:
    migrations.append("ALTER TABLE tasks ADD COLUMN recurrence_interval INTEGER DEFAULT 1")
    
if 'parent_task_id' not in columns:
    migrations.append("ALTER TABLE tasks ADD COLUMN parent_task_id INTEGER")

if not migrations:
    print("✅ All columns already exist!")
else:
    print(f"Adding {len(migrations)} new columns...")
    for sql in migrations:
        print(f"  - {sql}")
        cursor.execute(sql)
    
    conn.commit()
    print("✅ Database migration completed successfully!")

conn.close()
