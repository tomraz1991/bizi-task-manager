"""
Tests for workflow automation: studio prep task, daily workflow, stale task deletion.
"""
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from models import Episode, Task, Podcast, EpisodeStatus, TaskType, TaskStatus
from services.workflow_automation import (
    create_studio_preparation_task,
    delete_stale_studio_preparation_tasks,
    process_daily_workflow,
)


class TestCreateStudioPreparationTask:
    def test_creates_task_when_none_exists(self, db_session, sample_episode):
        task = create_studio_preparation_task(db_session, sample_episode)
        assert task is not None
        assert task.type == TaskType.STUDIO_PREPARATION
        assert task.status == TaskStatus.NOT_STARTED
        assert task.episode_id == sample_episode.id
        assert task.due_date is not None  # 1 hour before recording

    def test_idempotent_returns_existing(self, db_session, sample_episode):
        t1 = create_studio_preparation_task(db_session, sample_episode)
        t2 = create_studio_preparation_task(db_session, sample_episode)
        assert t1.id == t2.id
        count = db_session.query(Task).filter(
            Task.episode_id == sample_episode.id,
            Task.type == TaskType.STUDIO_PREPARATION,
        ).count()
        assert count == 1

    def test_episode_without_recording_date(self, db_session, sample_podcast):
        ep = Episode(
            podcast_id=sample_podcast.id,
            episode_number="1",
            recording_date=None,
            status=EpisodeStatus.NOT_STARTED,
        )
        db_session.add(ep)
        db_session.commit()
        db_session.refresh(ep)
        task = create_studio_preparation_task(db_session, ep)
        assert task is not None
        assert task.due_date is None


class TestDeleteStaleStudioPreparationTasks:
    def test_deletes_overdue_studio_prep_tasks(self, db_session, sample_episode):
        create_studio_preparation_task(db_session, sample_episode)
        # Set due_date to 2 days ago
        task = db_session.query(Task).filter(
            Task.episode_id == sample_episode.id,
            Task.type == TaskType.STUDIO_PREPARATION,
        ).first()
        task.due_date = (datetime.now(timezone.utc) - timedelta(days=2)).replace(tzinfo=None)
        db_session.commit()

        deleted = delete_stale_studio_preparation_tasks(db_session)
        assert deleted == 1
        remaining = db_session.query(Task).filter(
            Task.episode_id == sample_episode.id,
            Task.type == TaskType.STUDIO_PREPARATION,
        ).first()
        assert remaining is None

    def test_does_not_delete_recent_tasks(self, db_session, sample_episode):
        create_studio_preparation_task(db_session, sample_episode)
        deleted = delete_stale_studio_preparation_tasks(db_session)
        assert deleted == 0
        task = db_session.query(Task).filter(
            Task.episode_id == sample_episode.id,
            Task.type == TaskType.STUDIO_PREPARATION,
        ).first()
        assert task is not None


class TestProcessDailyWorkflow:
    def test_creates_studio_prep_for_todays_episodes(self, db_session, sample_episode):
        with patch("services.workflow_automation.get_todays_episodes_from_calendar") as m:
            m.return_value = [sample_episode]
            count = process_daily_workflow(db_session)
        assert count == 1
        task = db_session.query(Task).filter(
            Task.episode_id == sample_episode.id,
            Task.type == TaskType.STUDIO_PREPARATION,
        ).first()
        assert task is not None

    def test_returns_count_of_episodes_processed(self, db_session, sample_episode):
        with patch("services.workflow_automation.get_todays_episodes_from_calendar") as m:
            m.return_value = [sample_episode]
            count = process_daily_workflow(db_session)
        assert count == 1

    def test_zero_episodes(self, db_session):
        with patch("services.workflow_automation.get_todays_episodes_from_calendar") as m:
            m.return_value = []
            count = process_daily_workflow(db_session)
        assert count == 0
