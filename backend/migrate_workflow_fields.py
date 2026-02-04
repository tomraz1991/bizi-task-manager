"""
Migration script to add workflow automation fields.
"""
from sqlalchemy import text
from database import engine

def migrate_workflow_fields():
    """Add new fields for workflow automation."""
    with engine.connect() as conn:
        # Add default_studio_settings to podcasts table
        try:
            conn.execute(text("ALTER TABLE podcasts ADD COLUMN default_studio_settings TEXT"))
            print("Added default_studio_settings to podcasts table")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("Column default_studio_settings already exists in podcasts table")
            else:
                raise
        
        # Add studio_settings_override to episodes table
        try:
            conn.execute(text("ALTER TABLE episodes ADD COLUMN studio_settings_override TEXT"))
            print("Added studio_settings_override to episodes table")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("Column studio_settings_override already exists in episodes table")
            else:
                raise
        
        # Add client_approved_editing to episodes table
        try:
            conn.execute(text("ALTER TABLE episodes ADD COLUMN client_approved_editing TEXT DEFAULT 'pending'"))
            print("Added client_approved_editing to episodes table")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("Column client_approved_editing already exists in episodes table")
            else:
                raise
        
        # Add client_approved_reels to episodes table
        try:
            conn.execute(text("ALTER TABLE episodes ADD COLUMN client_approved_reels TEXT DEFAULT 'pending'"))
            print("Added client_approved_reels to episodes table")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("Column client_approved_reels already exists in episodes table")
            else:
                raise
        
        conn.commit()
        print("Migration completed successfully!")

if __name__ == "__main__":
    migrate_workflow_fields()
