"""
Migration script to add memory_card column to episodes.
Run once for existing databases: .venv/bin/python migrate_memory_card.py
"""
from sqlalchemy import text
from database import engine

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE episodes ADD COLUMN memory_card VARCHAR"))
            conn.commit()
            print("Added memory_card column to episodes table.")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("Column memory_card already exists.")
            else:
                raise

if __name__ == "__main__":
    migrate()
