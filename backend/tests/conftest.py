"""
Pytest fixtures for backend tests.
Uses in-memory SQLite and ensures DB is created from models.
"""
import os
import sys
from pathlib import Path

# Run from backend directory so imports resolve
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))
os.chdir(backend_dir)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import after path is set
from database import Base, get_db
from models import Podcast, PodcastAlias, Episode, User, Task, EpisodeStatus, TaskType, TaskStatus
from main import app
from fastapi.testclient import TestClient


# In-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    """Create a fresh in-memory engine per test."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    """Provide a DB session that rolls back after each test."""
    Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db_engine):
    """FastAPI TestClient with overridden get_db to use test DB."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    Base.metadata.create_all(bind=db_engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_podcast(db_session):
    """Create one podcast for matching tests."""
    p = Podcast(name="רוני וברק")
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


@pytest.fixture
def sample_podcast_with_alias(db_session):
    """Create a podcast and an alias (e.g. calendar title)."""
    p = Podcast(name="The Show")
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    a = PodcastAlias(podcast_id=p.id, alias="The Show - Givon Room")
    db_session.add(a)
    db_session.commit()
    return p


@pytest.fixture
def sample_episode(db_session, sample_podcast):
    """Create one episode for task/workflow tests."""
    from datetime import datetime, timezone
    e = Episode(
        podcast_id=sample_podcast.id,
        episode_number="33",
        recording_date=datetime.now(timezone.utc),
        status=EpisodeStatus.NOT_STARTED,
    )
    db_session.add(e)
    db_session.commit()
    db_session.refresh(e)
    return e
