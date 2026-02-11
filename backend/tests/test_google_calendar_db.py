"""
Tests for Google Calendar DB logic: podcast lookup, episode create/update.
"""
import sys
from pathlib import Path
from datetime import datetime, timezone

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from models import Podcast, PodcastAlias, Episode, EpisodeStatus
from services.google_calendar import (
    find_podcast_by_name_or_alias,
    find_podcast_from_event_title,
    find_or_create_podcast,
    create_or_update_episode_from_event,
)


class TestFindPodcastByNameOrAlias:
    def test_exact_name_match(self, db_session, sample_podcast):
        found = find_podcast_by_name_or_alias(db_session, "רוני וברק")
        assert found is not None
        assert found.id == sample_podcast.id

    def test_case_insensitive_name_match(self, db_session, sample_podcast):
        found = find_podcast_by_name_or_alias(db_session, "רוני וברק".upper())
        assert found is not None
        assert found.id == sample_podcast.id

    def test_alias_match(self, db_session, sample_podcast_with_alias):
        found = find_podcast_by_name_or_alias(db_session, "The Show - Givon Room")
        assert found is not None
        assert found.name == "The Show"

    def test_no_match_returns_none(self, db_session, sample_podcast):
        found = find_podcast_by_name_or_alias(db_session, "Unknown Podcast")
        assert found is None

    def test_empty_name_returns_none(self, db_session):
        assert find_podcast_by_name_or_alias(db_session, "") is None
        assert find_podcast_by_name_or_alias(db_session, None) is None


class TestFindPodcastFromEventTitle:
    def test_exact_title_match_via_alias(self, db_session, sample_podcast_with_alias):
        found = find_podcast_from_event_title(db_session, "The Show - Givon Room")
        assert found is not None
        assert found.name == "The Show"

    def test_substring_match_longest_wins(self, db_session):
        p1 = Podcast(name="The")
        p2 = Podcast(name="The Show")
        db_session.add_all([p1, p2])
        db_session.commit()
        found = find_podcast_from_event_title(db_session, "The Show - פרק 1")
        assert found is not None
        assert found.name == "The Show"

    def test_empty_title_returns_none(self, db_session):
        assert find_podcast_from_event_title(db_session, "") is None
        assert find_podcast_from_event_title(db_session, None) is None


class TestFindOrCreatePodcast:
    def test_returns_existing(self, db_session, sample_podcast):
        found = find_or_create_podcast(db_session, "רוני וברק")
        assert found is not None
        assert found.id == sample_podcast.id
        count = db_session.query(Podcast).count()
        assert count == 1

    def test_creates_new(self, db_session):
        found = find_or_create_podcast(db_session, "New Podcast")
        assert found is not None
        assert found.name == "New Podcast"
        assert db_session.query(Podcast).filter(Podcast.name == "New Podcast").first() is not None

    def test_empty_name_returns_none(self, db_session):
        assert find_or_create_podcast(db_session, "") is None
        assert find_or_create_podcast(db_session, None) is None


class TestCreateOrUpdateEpisodeFromEvent:
    def test_creates_new_episode(self, db_session, sample_podcast):
        event_data = {
            "podcast_name": "רוני וברק",
            "episode_number": "33",
            "recording_date": datetime(2025, 2, 11, 10, 0, 0, tzinfo=timezone.utc),
            "studio": "Room A",
            "guest_names": None,
            "notes": None,
        }
        ep = create_or_update_episode_from_event(db_session, event_data, sample_podcast)
        assert ep is not None
        assert ep.episode_number == "33"
        assert ep.studio == "Room A"
        assert ep.status == EpisodeStatus.NOT_STARTED

    def test_updates_existing_episode_same_day(self, db_session, sample_podcast):
        rec_date = datetime(2025, 2, 11, 10, 0, 0, tzinfo=timezone.utc)
        existing = Episode(
            podcast_id=sample_podcast.id,
            episode_number="33",
            recording_date=rec_date,
            status=EpisodeStatus.NOT_STARTED,
        )
        db_session.add(existing)
        db_session.commit()
        db_session.refresh(existing)

        event_data = {
            "episode_number": "33",
            "recording_date": rec_date,
            "studio": "Updated Studio",
            "guest_names": "Guest",
            "notes": "Notes",
        }
        ep = create_or_update_episode_from_event(db_session, event_data, sample_podcast)
        assert ep is not None
        assert ep.id == existing.id
        assert ep.studio == "Updated Studio"
        assert ep.guest_names == "Guest"

    def test_does_not_overwrite_existing_studio_if_event_has_studio(self, db_session, sample_podcast):
        rec_date = datetime(2025, 2, 11, 10, 0, 0, tzinfo=timezone.utc)
        existing = Episode(
            podcast_id=sample_podcast.id,
            episode_number="33",
            recording_date=rec_date,
            studio="Existing Studio",
        )
        db_session.add(existing)
        db_session.commit()
        db_session.refresh(existing)
        event_data = {
            "episode_number": "33",
            "recording_date": rec_date,
            "studio": "Event Studio",
        }
        ep = create_or_update_episode_from_event(db_session, event_data, sample_podcast)
        assert ep.studio == "Existing Studio"  # only fill if not set

    def test_creates_second_episode_different_number_same_day(self, db_session, sample_podcast):
        rec_date = datetime(2025, 2, 11, 10, 0, 0, tzinfo=timezone.utc)
        event_data_33 = {
            "episode_number": "33",
            "recording_date": rec_date,
            "studio": None,
            "guest_names": None,
            "notes": None,
        }
        event_data_34 = {
            "episode_number": "34",
            "recording_date": rec_date,
            "studio": None,
            "guest_names": None,
            "notes": None,
        }
        ep1 = create_or_update_episode_from_event(db_session, event_data_33, sample_podcast)
        ep2 = create_or_update_episode_from_event(db_session, event_data_34, sample_podcast)
        assert ep1.id != ep2.id
        assert ep1.episode_number == "33"
        assert ep2.episode_number == "34"
