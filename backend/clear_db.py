"""
Clear all data from the database.
This will delete all records from all tables but keep the table structure.

To clear Render PostgreSQL from your machine:
  1. In Render Dashboard → your PostgreSQL → Connect → copy "External Database URL"
  2. In terminal: cd backend && DATABASE_URL="postgresql://..." python clear_db.py
"""
import os
from database import engine
from sqlalchemy import text

def clear_database():
    """Clear all data from all tables."""
    db_url = os.environ.get("DATABASE_URL", "")
    if db_url and "render.com" in db_url:
        confirm = input("This will DELETE ALL DATA in your Render PostgreSQL database. Type 'yes' to continue: ")
        if confirm.strip().lower() != "yes":
            print("Aborted.")
            return

    print("Clearing database...")

    with engine.connect() as conn:
        # Delete all records (order respects foreign keys)
        for table in ("tasks", "episodes", "podcasts", "users"):
            print(f"Deleting {table}...")
            conn.execute(text(f"DELETE FROM {table}"))
        conn.commit()

    print("\n✅ Database cleared. Tables are empty; you can re-import CSV.")

if __name__ == "__main__":
    clear_database()
