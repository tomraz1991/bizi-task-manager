"""
Database migration script to add new fields to existing database.
Run this after updating models to add new columns.
"""
from sqlalchemy import text
from database import engine

def migrate_database():
    """Add new columns to existing tables if they don't exist."""
    with engine.connect() as conn:
        # Check and add episode columns
        try:
            # Add card_name if it doesn't exist
            conn.execute(text("ALTER TABLE episodes ADD COLUMN card_name VARCHAR"))
            print("Added card_name column to episodes")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"Error adding card_name: {e}")
        
        try:
            # Add recording_engineer_id if it doesn't exist
            conn.execute(text("ALTER TABLE episodes ADD COLUMN recording_engineer_id VARCHAR"))
            print("Added recording_engineer_id column to episodes")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"Error adding recording_engineer_id: {e}")
        
        try:
            # Add editing_engineer_id if it doesn't exist
            conn.execute(text("ALTER TABLE episodes ADD COLUMN editing_engineer_id VARCHAR"))
            print("Added editing_engineer_id column to episodes")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"Error adding editing_engineer_id: {e}")
        
        try:
            # Add reels_engineer_id if it doesn't exist
            conn.execute(text("ALTER TABLE episodes ADD COLUMN reels_engineer_id VARCHAR"))
            print("Added reels_engineer_id column to episodes")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"Error adding reels_engineer_id: {e}")
        
        try:
            # Add reels_notes if it doesn't exist
            conn.execute(text("ALTER TABLE episodes ADD COLUMN reels_notes TEXT"))
            print("Added reels_notes column to episodes")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"Error adding reels_notes: {e}")
        
        # Update tasks table - rename owner_id to assigned_to if needed
        try:
            # Check if owner_id exists and assigned_to doesn't
            result = conn.execute(text("PRAGMA table_info(tasks)"))
            columns = [row[1] for row in result]
            
            if 'owner_id' in columns and 'assigned_to' not in columns:
                # SQLite doesn't support RENAME COLUMN directly, so we need to recreate
                # For now, just add assigned_to and we'll migrate data
                conn.execute(text("ALTER TABLE tasks ADD COLUMN assigned_to VARCHAR"))
                # Copy data from owner_id to assigned_to
                conn.execute(text("UPDATE tasks SET assigned_to = owner_id WHERE owner_id IS NOT NULL"))
                print("Added assigned_to column and migrated data from owner_id")
            elif 'assigned_to' not in columns:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN assigned_to VARCHAR"))
                print("Added assigned_to column to tasks")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"Error updating tasks table: {e}")
        
        # Add foreign key constraints if they don't exist (SQLite has limited FK support)
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_episodes_recording_engineer ON episodes(recording_engineer_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_episodes_editing_engineer ON episodes(editing_engineer_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_episodes_reels_engineer ON episodes(reels_engineer_id)"))
            print("Created indexes for engineer fields")
        except Exception as e:
            print(f"Error creating indexes: {e}")
        
        conn.commit()
        print("\n✅ Database migration completed!")

if __name__ == "__main__":
    migrate_database()
