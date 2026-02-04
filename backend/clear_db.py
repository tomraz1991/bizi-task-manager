"""
Clear all data from the database.
This will delete all records from all tables but keep the table structure.
"""
from database import engine, Base
from models import Podcast, Episode, Task, User
from sqlalchemy.orm import Session
from sqlalchemy import text

def clear_database():
    """Clear all data from all tables."""
    print("Clearing database...")
    
    with engine.connect() as conn:
        # Delete all records (in correct order to respect foreign keys)
        print("Deleting tasks...")
        conn.execute(text("DELETE FROM tasks"))
        
        print("Deleting episodes...")
        conn.execute(text("DELETE FROM episodes"))
        
        print("Deleting podcasts...")
        conn.execute(text("DELETE FROM podcasts"))
        
        print("Deleting users...")
        conn.execute(text("DELETE FROM users"))
        
        conn.commit()
        print("\n✅ Database cleared successfully!")
        print("All tables are now empty. You can re-import your CSV file.")

if __name__ == "__main__":
    clear_database()
