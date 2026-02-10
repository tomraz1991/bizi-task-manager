"""
Migration: add SENT_TO_CLIENT to PostgreSQL taskstatus enum.
Run once on Render (or any PostgreSQL DB) after deploying the TaskStatus.SENT_TO_CLIENT change.

  cd backend && .venv/bin/python migrate_task_status_sent_to_client.py

Uses DATABASE_URL from environment. For Render, use the External Database URL when running locally.
"""
import os
from sqlalchemy import text
from database import engine

def migrate():
    url = os.environ.get("DATABASE_URL", "")
    if "postgresql" not in url and "postgres" not in url:
        print("Not PostgreSQL; no enum migration needed (SQLite uses string).")
        return
    with engine.connect() as conn:
        # PostgreSQL: add new value to existing enum (SQLAlchemy creates type "taskstatus")
        try:
            conn.execute(text("ALTER TYPE taskstatus ADD VALUE IF NOT EXISTS 'sent_to_client'"))
            conn.commit()
            print("Added 'sent_to_client' to taskstatus enum.")
        except Exception as e:
            # Older PostgreSQL: IF NOT EXISTS not supported, try without
            if "syntax" in str(e).lower() or "not exist" in str(e).lower():
                try:
                    conn.execute(text("ALTER TYPE taskstatus ADD VALUE 'sent_to_client'"))
                    conn.commit()
                    print("Added 'sent_to_client' to taskstatus enum.")
                except Exception as e2:
                    if "already exists" in str(e2).lower():
                        print("Value 'sent_to_client' already in taskstatus enum.")
                        conn.rollback()
                    else:
                        conn.rollback()
                        raise
            else:
                conn.rollback()
                raise

if __name__ == "__main__":
    migrate()
