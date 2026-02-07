"""
Migration script to add podcast_aliases table.
Run once for existing databases: .venv/bin/python migrate_podcast_aliases.py
"""
from sqlalchemy import text
from database import engine

def migrate():
    with engine.connect() as conn:
        # SQLite and PostgreSQL compatible CREATE TABLE
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS podcast_aliases (
                id VARCHAR NOT NULL PRIMARY KEY,
                podcast_id VARCHAR NOT NULL,
                alias VARCHAR NOT NULL UNIQUE,
                FOREIGN KEY(podcast_id) REFERENCES podcasts (id) ON DELETE CASCADE
            )
        """))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_podcast_aliases_podcast_id ON podcast_aliases (podcast_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_podcast_aliases_alias ON podcast_aliases (alias)"))
        conn.commit()
        print("Created podcast_aliases table.")

if __name__ == "__main__":
    migrate()
