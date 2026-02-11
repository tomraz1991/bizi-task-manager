"""
API tests for workflow endpoints: POST /daily, POST /sync-calendar.
Tests call route handlers directly with test DB to avoid TestClient/httpx version issues.
"""
import sys
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from database import Base
from models import Podcast, Episode, EpisodeStatus
from api.workflow import trigger_daily_workflow, sync_calendar


@pytest.mark.asyncio
class TestWorkflowDailyEndpoint:
    async def test_returns_200_and_structure(self, db_engine):
        Base.metadata.create_all(bind=db_engine)
        Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
        session = Session()
        try:
            p = Podcast(name="Test Podcast")
            session.add(p)
            session.commit()
            session.refresh(p)
            e = Episode(
                podcast_id=p.id,
                episode_number="1",
                recording_date=datetime.now(timezone.utc),
                status=EpisodeStatus.NOT_STARTED,
            )
            session.add(e)
            session.commit()
        finally:
            session.close()

        session2 = Session()
        try:
            with patch("services.google_calendar.settings") as mock_settings:
                mock_settings.GOOGLE_CALENDAR_ENABLED = False
                with patch("services.google_calendar.GOOGLE_API_AVAILABLE", False):
                    response = await trigger_daily_workflow(session2)
            assert "message" in response
        finally:
            session2.close()
        assert "episodes_processed" in response
        assert response["episodes_processed"] >= 1

    async def test_returns_500_when_workflow_raises(self, db_engine):
        Base.metadata.create_all(bind=db_engine)
        Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
        session = Session()
        try:
            with patch("api.workflow.process_daily_workflow") as m:
                m.side_effect = RuntimeError("Simulated failure")
                with pytest.raises(HTTPException) as exc_info:
                    await trigger_daily_workflow(session)
            assert exc_info.value.status_code == 500
            assert exc_info.value.detail and "Simulated" in str(exc_info.value.detail)
        finally:
            session.close()


@pytest.mark.asyncio
class TestWorkflowSyncCalendarEndpoint:
    async def test_returns_200_and_structure(self, db_engine):
        Base.metadata.create_all(bind=db_engine)
        Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
        session = Session()
        try:
            response = await sync_calendar(None, session)
            assert "message" in response
            assert "episodes_synced" in response
            assert isinstance(response["episodes_synced"], int)
        finally:
            session.close()

    async def test_accepts_days_ahead_query(self, db_engine):
        Base.metadata.create_all(bind=db_engine)
        Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
        session = Session()
        try:
            response = await sync_calendar(3, session)
            assert "episodes_synced" in response
        finally:
            session.close()

    async def test_returns_500_when_sync_raises(self, db_engine):
        Base.metadata.create_all(bind=db_engine)
        Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
        session = Session()
        try:
            with patch("api.workflow.sync_calendar_to_database") as m:
                m.side_effect = ValueError("Simulated sync failure")
                with pytest.raises(HTTPException) as exc_info:
                    await sync_calendar(None, session)
            assert exc_info.value.status_code == 500
        finally:
            session.close()
