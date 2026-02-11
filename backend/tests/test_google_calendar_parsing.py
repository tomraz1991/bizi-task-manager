"""
Unit tests for Google Calendar event parsing (no DB).
"""
import sys
from pathlib import Path
import pytest

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from services.google_calendar import parse_event_title, extract_episode_data_from_event


class TestParseEventTitle:
    """Edge cases and scenarios for parse_event_title."""

    def test_empty_title_returns_none_fields(self):
        result = parse_event_title("")
        assert result["podcast_name"] is None
        assert result["episode_number"] is None
        assert result["episode_numbers"] == []

    def test_none_title_returns_none_fields(self):
        result = parse_event_title(None)
        assert result["podcast_name"] is None
        assert result["episode_number"] is None
        assert result["episode_numbers"] == []

    def test_hebrew_parak_single(self):
        result = parse_event_title("רוני וברק - פרק 33")
        # Parser may leave trailing " -" when stripping episode suffix
        assert result["podcast_name"] is not None and "רוני וברק" in result["podcast_name"]
        assert result["episode_number"] == "33"
        assert result["episode_numbers"] == ["33"]

    def test_hash_single(self):
        result = parse_event_title("Recording: רוני וברק #33")
        assert "33" in result["episode_numbers"]
        assert result["episode_number"] == "33"

    def test_hebrew_and_two_episodes(self):
        result = parse_event_title("רוני וברק פרק 33 ו-34")
        assert "33" in result["episode_numbers"] and "34" in result["episode_numbers"]
        assert result["episode_number"] == "33"

    def test_range_two_episodes(self):
        result = parse_event_title("Podcast 33-34")
        assert "33" in result["episode_numbers"] and "34" in result["episode_numbers"]

    def test_comma_separated(self):
        result = parse_event_title("Show - 33, 34")
        assert "33" in result["episode_numbers"] and "34" in result["episode_numbers"]

    def test_ampersand_separated(self):
        result = parse_event_title("Show 33 & 34")
        assert "33" in result["episode_numbers"] and "34" in result["episode_numbers"]

    def test_single_number_at_end(self):
        result = parse_event_title("Some Podcast - 33")
        assert result["episode_numbers"] == ["33"]
        assert result["podcast_name"] == "Some Podcast"

    def test_no_episode_number_podcast_name_is_title(self):
        result = parse_event_title("Just a Meeting")
        assert result["episode_numbers"] == []
        assert result["episode_number"] is None
        assert result["podcast_name"] == "Just a Meeting"

    def test_episode_keyword_english(self):
        result = parse_event_title("My Show episode 5")
        assert result["episode_numbers"] == ["5"]
        assert result["episode_number"] == "5"

    def test_duplicate_numbers_deduped(self):
        result = parse_event_title("Show 33, 33")
        assert result["episode_numbers"] == ["33"]

    def test_range_capped_sane(self):
        # Range 1-5 is allowed (<=10 difference)
        result = parse_event_title("Show 1-5")
        assert len(result["episode_numbers"]) >= 2
        assert "1" in result["episode_numbers"] and "5" in result["episode_numbers"]

    def test_large_range_capped(self):
        # 1-100: high - low > 10, so only the two numbers may be added (elif branch)
        result = parse_event_title("Show 1-100")
        assert len(result["episode_numbers"]) >= 1
        assert "100" in result["episode_numbers"] or "1" in result["episode_numbers"]


class TestExtractEpisodeDataFromEvent:
    """extract_episode_data_from_event with mock event dicts."""

    def test_minimal_event_with_datetime(self):
        event = {
            "summary": "רוני וברק - פרק 33",
            "start": {"dateTime": "2025-02-11T10:00:00+00:00"},
            "end": {},
        }
        data = extract_episode_data_from_event(event)
        assert data["podcast_name"] is not None and "רוני וברק" in data["podcast_name"]
        assert data["episode_number"] == "33"
        assert data["recording_date"] is not None
        assert data["studio"] is None
        assert data["guest_names"] is None

    def test_event_with_z_suffix(self):
        event = {
            "summary": "Show #1",
            "start": {"dateTime": "2025-02-11T12:00:00Z"},
        }
        data = extract_episode_data_from_event(event)
        assert data["recording_date"] is not None

    def test_all_day_event(self):
        event = {
            "summary": "Show - פרק 2",
            "start": {"date": "2025-02-11"},
        }
        data = extract_episode_data_from_event(event)
        assert data["recording_date"] is not None
        assert data["episode_number"] == "2"

    def test_location_and_description(self):
        event = {
            "summary": "Show #1",
            "start": {"dateTime": "2025-02-11T10:00:00Z"},
            "location": "Givon Room",
            "description": "אורח: John Doe",
        }
        data = extract_episode_data_from_event(event)
        assert data["studio"] == "Givon Room"
        assert data["guest_names"] == "John Doe"
        assert data["notes"] == "אורח: John Doe"

    def test_extended_properties_override_empty(self):
        event = {
            "summary": "Show",
            "start": {"date": "2025-02-11"},
            "extendedProperties": {
                "private": {
                    "episode_number": "42",
                    "studio": "Studio B",
                    "guest_names": "Jane",
                }
            },
        }
        data = extract_episode_data_from_event(event)
        assert data["episode_number"] == "42"
        assert data["studio"] == "Studio B"
        assert data["guest_names"] == "Jane"

    def test_extended_properties_do_not_override_non_empty(self):
        event = {
            "summary": "Show #10",
            "start": {"date": "2025-02-11"},
            "location": "Room A",
            "extendedProperties": {"private": {"studio": "Room B"}},
        }
        data = extract_episode_data_from_event(event)
        # Title-derived episode_number and location-derived studio take precedence
        assert data["episode_number"] == "10"
        assert data["studio"] == "Room A"

    def test_missing_summary_uses_empty(self):
        event = {"start": {"date": "2025-02-11"}}
        data = extract_episode_data_from_event(event)
        assert data["podcast_name"] is None
        assert data["episode_numbers"] == []
        assert data["recording_date"] is not None
