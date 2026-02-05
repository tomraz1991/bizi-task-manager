"""
Migration script to add tasks_time_allowance_days column to podcasts.
Run once for existing databases: DATABASE_URL="..." .venv/bin/python migrate_podcast_tasks_allowance.py
"""
from sqlalchemy import text
from database import engine

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE podcasts ADD COLUMN tasks_time_allowance_days VARCHAR"))
            conn.commit()
            print("Added tasks_time_allowance_days column to podcasts table.")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("Column tasks_time_allowance_days already exists.")
            else:
                raise

if __name__ == "__main__":
    migrate()
