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
            err = str(e).lower()
            if "duplicate column" in err or "already exists" in err or "duplicate column name" in err:
                print("Column tasks_time_allowance_days already exists.")
            else:
                raise

if __name__ == "__main__":
    migrate()
