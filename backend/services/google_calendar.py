"""
Google Calendar integration service.
"""
import json
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models import Episode, Podcast, PodcastAlias, EpisodeStatus
from config import settings

logger = logging.getLogger(__name__)

# Try to import Google Calendar API, but handle gracefully if not available
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    logger.warning("Google Calendar API libraries not installed. Calendar integration disabled.")


def get_calendar_service():
    """
    Authenticate and return Google Calendar service object.
    
    Returns:
        Google Calendar API service object or None if unavailable
    """
    if not GOOGLE_API_AVAILABLE:
        logger.warning("Google Calendar API not available")
        return None
    
    if not settings.GOOGLE_CALENDAR_ENABLED:
        logger.debug("Google Calendar integration is disabled")
        return None

    credentials = None
    if settings.GOOGLE_CREDENTIALS_JSON:
        try:
            info = json.loads(settings.GOOGLE_CREDENTIALS_JSON)
            credentials = service_account.Credentials.from_service_account_info(
                info,
                scopes=['https://www.googleapis.com/auth/calendar.readonly']
            )
        except Exception as e:
            logger.error(f"Failed to parse GOOGLE_CREDENTIALS_JSON: {e}", exc_info=True)
            return None
    elif settings.GOOGLE_CREDENTIALS_PATH:
        credentials_path = Path(settings.GOOGLE_CREDENTIALS_PATH)
        if not credentials_path.exists():
            logger.error(f"Google credentials file not found: {credentials_path}")
            return None
        try:
            credentials = service_account.Credentials.from_service_account_file(
                str(credentials_path),
                scopes=['https://www.googleapis.com/auth/calendar.readonly']
            )
        except Exception as e:
            logger.error(f"Failed to load credentials from file: {e}", exc_info=True)
            return None
    else:
        logger.warning("Neither GOOGLE_CREDENTIALS_JSON nor GOOGLE_CREDENTIALS_PATH configured")
        return None

    try:
        service = build('calendar', 'v3', credentials=credentials)
        logger.info("Google Calendar service initialized successfully")
        return service
    except Exception as e:
        logger.error(f"Failed to initialize Google Calendar service: {e}", exc_info=True)
        return None


def parse_event_title(title: str) -> Dict[str, Optional[str]]:
    """
    Parse calendar event title to extract podcast name and episode number.
    
    Supports multiple formats:
    - "רוני וברק - פרק 33"
    - "Recording: רוני וברק #33"
    - "רוני וברק פרק 33"
    - "רוני וברק - 33"
    
    Args:
        title: Calendar event title
        
    Returns:
        Dictionary with 'podcast_name' and 'episode_number'
    """
    result = {
        'podcast_name': None,
        'episode_number': None
    }
    
    if not title:
        return result
    
    # Try to extract episode number (various patterns)
    episode_patterns = [
        r'פרק\s*(\d+)',  # "פרק 33"
        r'#(\d+)',        # "#33"
        r'episode\s*(\d+)',  # "episode 33"
        r'ep\s*(\d+)',   # "ep 33"
        r'\s+(\d+)\s*$',  # "33" at end
        r'[-–]\s*(\d+)',  # "- 33" or "– 33"
    ]
    
    episode_number = None
    for pattern in episode_patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            episode_number = match.group(1)
            break
    
    # Extract podcast name (everything before episode number)
    if episode_number:
        # Remove episode number and separators
        podcast_name = re.sub(
            r'\s*(פרק|#|episode|ep)\s*\d+.*$',
            '',
            title,
            flags=re.IGNORECASE
        )
        podcast_name = re.sub(r'[-–]\s*\d+.*$', '', podcast_name)
        podcast_name = re.sub(r'\s+\d+\s*$', '', podcast_name)
        podcast_name = podcast_name.strip()
    else:
        # No episode number found, use entire title as podcast name
        podcast_name = title.strip()
    
    result['podcast_name'] = podcast_name if podcast_name else None
    result['episode_number'] = episode_number
    
    return result


def extract_episode_data_from_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract episode data from Google Calendar event.
    
    Args:
        event: Google Calendar event object
        
    Returns:
        Dictionary with episode data
    """
    data = {
        'podcast_name': None,
        'episode_number': None,
        'recording_date': None,
        'studio': None,
        'guest_names': None,
        'notes': None,
    }
    
    # Parse title
    title = event.get('summary', '')
    parsed = parse_event_title(title)
    data['podcast_name'] = parsed['podcast_name']
    data['episode_number'] = parsed['episode_number']
    
    # Extract recording date/time
    start = event.get('start', {})
    if 'dateTime' in start:
        # Full datetime
        data['recording_date'] = datetime.fromisoformat(
            start['dateTime'].replace('Z', '+00:00')
        )
    elif 'date' in start:
        # All-day event
        data['recording_date'] = datetime.fromisoformat(
            start['date'] + 'T00:00:00+00:00'
        )
    
    # Extract location (studio)
    data['studio'] = event.get('location')
    
    # Extract description
    description = event.get('description', '')
    data['notes'] = description
    
    # Try to extract guest names from description
    guest_patterns = [
        r'אורח[ים]?[:\s]+([^\n]+)',
        r'guest[s]?[:\s]+([^\n]+)',
        r'with\s+([^\n]+)',
    ]
    for pattern in guest_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            data['guest_names'] = match.group(1).strip()
            break
    
    # Check extended properties for episode metadata
    extended_properties = event.get('extendedProperties', {})
    private_props = extended_properties.get('private', {})
    
    if 'podcast_id' in private_props:
        data['podcast_id'] = private_props['podcast_id']
    if 'episode_number' in private_props and not data['episode_number']:
        data['episode_number'] = private_props['episode_number']
    if 'studio' in private_props and not data['studio']:
        data['studio'] = private_props['studio']
    if 'guest_names' in private_props and not data['guest_names']:
        data['guest_names'] = private_props['guest_names']
    
    return data


def find_podcast_by_name_or_alias(db: Session, podcast_name: str) -> Optional[Podcast]:
    """
    Find a podcast by exact name or by alias (e.g. calendar event title).
    """
    if not podcast_name:
        return None
    name = podcast_name.strip()
    # Exact name match
    podcast = db.query(Podcast).filter(Podcast.name == name).first()
    if podcast:
        return podcast
    # Case-insensitive name match
    podcast = db.query(Podcast).filter(Podcast.name.ilike(name)).first()
    if podcast:
        return podcast
    # Alias match (exact then case-insensitive)
    alias_row = db.query(PodcastAlias).filter(PodcastAlias.alias == name).first()
    if alias_row:
        return db.query(Podcast).filter(Podcast.id == alias_row.podcast_id).first()
    alias_row = db.query(PodcastAlias).filter(PodcastAlias.alias.ilike(name)).first()
    if alias_row:
        return db.query(Podcast).filter(Podcast.id == alias_row.podcast_id).first()
    return None


def find_or_create_podcast(db: Session, podcast_name: str) -> Optional[Podcast]:
    """
    Find existing podcast by name or alias, or create new one.
    
    Args:
        db: Database session
        podcast_name: Name of the podcast (or alias from calendar event)
        
    Returns:
        Podcast object or None if creation fails
    """
    if not podcast_name:
        return None

    # Resolve by name or alias first
    podcast = find_podcast_by_name_or_alias(db, podcast_name)
    if podcast:
        return podcast

    # Create new podcast
    logger.info(f"Creating new podcast: {podcast_name}")
    podcast = Podcast(name=podcast_name)
    db.add(podcast)
    try:
        db.commit()
        db.refresh(podcast)
        logger.info(f"Created podcast {podcast.id}: {podcast_name}")
        return podcast
    except Exception as e:
        logger.error(f"Failed to create podcast: {e}", exc_info=True)
        db.rollback()
        return None


def create_or_update_episode_from_event(
    db: Session,
    event_data: Dict[str, Any],
    podcast: Podcast
) -> Optional[Episode]:
    """
    Create or update episode from calendar event data.
    
    Args:
        db: Database session
        event_data: Extracted event data
        podcast: Podcast object
        
    Returns:
        Episode object or None if creation fails
    """
    # Check if episode already exists
    # Match by podcast_id, episode_number, and recording_date (within same day)
    episode = None
    if event_data.get('episode_number') and event_data.get('recording_date'):
        recording_date = event_data['recording_date']
        day_start = recording_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        episode = db.query(Episode).filter(
            and_(
                Episode.podcast_id == podcast.id,
                Episode.episode_number == event_data['episode_number'],
                Episode.recording_date >= day_start,
                Episode.recording_date < day_end
            )
        ).first()
    
    if episode:
        # Update existing episode
        logger.info(f"Updating existing episode {episode.id} from calendar event")
        if event_data.get('recording_date'):
            episode.recording_date = event_data['recording_date']
        if event_data.get('studio') and not episode.studio:
            episode.studio = event_data['studio']
        if event_data.get('guest_names') and not episode.guest_names:
            episode.guest_names = event_data['guest_names']
        if event_data.get('notes') and not episode.episode_notes:
            episode.episode_notes = event_data['notes']
    else:
        # Create new episode
        logger.info(f"Creating new episode for podcast {podcast.name}")
        episode = Episode(
            podcast_id=podcast.id,
            episode_number=event_data.get('episode_number'),
            recording_date=event_data.get('recording_date'),
            studio=event_data.get('studio'),
            guest_names=event_data.get('guest_names'),
            episode_notes=event_data.get('notes'),
            status=EpisodeStatus.NOT_STARTED
        )
        db.add(episode)
    
    try:
        db.commit()
        db.refresh(episode)
        return episode
    except Exception as e:
        logger.error(f"Failed to create/update episode: {e}", exc_info=True)
        db.rollback()
        return None


def get_todays_episodes_from_calendar(db: Session) -> List[Episode]:
    """
    Get episodes scheduled for today from Google Calendar.
    
    If Google Calendar is enabled and configured, fetches events from calendar.
    Otherwise, falls back to querying database for today's episodes.
    
    Args:
        db: Database session
        
    Returns:
        List of Episode objects scheduled for today
    """
    # If Google Calendar is not enabled, fall back to database query
    if not settings.GOOGLE_CALENDAR_ENABLED or not GOOGLE_API_AVAILABLE:
        logger.debug("Google Calendar disabled, querying database")
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        episodes = db.query(Episode).filter(
            and_(
                Episode.recording_date >= today_start,
                Episode.recording_date < today_end
            )
        ).all()
        
        logger.info(f"Found {len(episodes)} episodes scheduled for today in database")
        return episodes
    
    # Get calendar service
    service = get_calendar_service()
    if not service:
        logger.warning("Could not initialize Google Calendar service, falling back to database")
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        episodes = db.query(Episode).filter(
            and_(
                Episode.recording_date >= today_start,
                Episode.recording_date < today_end
            )
        ).all()
        return episodes
    
    # Query calendar for today's events
    try:
        # UTC date range for today (RFC 3339 format; avoid double timezone suffix)
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        def to_rfc3339_utc(dt):
            return dt.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

        time_min = to_rfc3339_utc(today_start)
        time_max = to_rfc3339_utc(today_end)
        
        logger.info(f"Fetching calendar events from {time_min} to {time_max}")
        
        events_result = service.events().list(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime',
        ).execute()
        
        events = events_result.get('items', [])
        logger.info(f"Found {len(events)} calendar events for today")
        
        episodes = []
        for event in events:
            try:
                # Extract episode data from event
                event_data = extract_episode_data_from_event(event)
                
                if not event_data.get('podcast_name'):
                    logger.debug(f"Skipping event '{event.get('summary')}' - no podcast name found")
                    continue
                
                # Only import if podcast is recognized (name or alias); do not create new podcasts
                podcast = find_podcast_by_name_or_alias(db, event_data['podcast_name'])
                if not podcast:
                    logger.info(f"Skipping event '{event.get('summary')}' - podcast not recognized: {event_data['podcast_name']}")
                    continue
                
                # Create or update episode
                episode = create_or_update_episode_from_event(db, event_data, podcast)
                if episode:
                    episodes.append(episode)
                    logger.info(f"Processed episode: {podcast.name} - {event_data.get('episode_number', 'N/A')}")
                
            except Exception as e:
                logger.error(f"Error processing calendar event {event.get('id')}: {e}", exc_info=True)
                continue
        
        logger.info(f"Successfully processed {len(episodes)} episodes from Google Calendar")
        return episodes
        
    except HttpError as e:
        logger.error(f"Google Calendar API error: {e}", exc_info=True)
        # Fall back to database query
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        episodes = db.query(Episode).filter(
            and_(
                Episode.recording_date >= today_start,
                Episode.recording_date < today_end
            )
        ).all()
        return episodes
    except Exception as e:
        logger.error(f"Unexpected error fetching calendar events: {e}", exc_info=True)
        # Fall back to database query
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        episodes = db.query(Episode).filter(
            and_(
                Episode.recording_date >= today_start,
                Episode.recording_date < today_end
            )
        ).all()
        return episodes


def sync_calendar_to_database(db: Session, days_ahead: Optional[int] = None) -> int:
    """
    Sync Google Calendar events to database episodes.
    
    Args:
        db: Database session
        days_ahead: Number of days ahead to sync (defaults to GOOGLE_CALENDAR_LOOKAHEAD_DAYS)
        
    Returns:
        Number of episodes synced
    """
    if not settings.GOOGLE_CALENDAR_ENABLED or not GOOGLE_API_AVAILABLE:
        logger.warning("Google Calendar sync disabled")
        return 0
    
    service = get_calendar_service()
    if not service:
        logger.warning("Could not initialize Google Calendar service")
        return 0
    
    days_ahead = days_ahead or settings.GOOGLE_CALENDAR_LOOKAHEAD_DAYS
    
    try:
        # UTC date range, RFC 3339 format (avoid double timezone suffix)
        now = datetime.now(timezone.utc)
        end = now + timedelta(days=days_ahead)

        def to_rfc3339_utc(dt):
            return dt.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

        time_min = to_rfc3339_utc(now)
        time_max = to_rfc3339_utc(end)
        
        logger.info(f"Syncing calendar events from {time_min} to {time_max}")
        
        events_result = service.events().list(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime',
        ).execute()
        
        events = events_result.get('items', [])
        logger.info(f"Found {len(events)} calendar events to sync")
        
        synced_count = 0
        for event in events:
            try:
                # Extract episode data from event
                event_data = extract_episode_data_from_event(event)
                
                if not event_data.get('podcast_name'):
                    continue
                
                # Only import if podcast is recognized (name or alias); do not create new podcasts
                podcast = find_podcast_by_name_or_alias(db, event_data['podcast_name'])
                if not podcast:
                    logger.debug(f"Skipping event - podcast not recognized: {event_data['podcast_name']}")
                    continue
                
                # Create or update episode
                episode = create_or_update_episode_from_event(db, event_data, podcast)
                if episode:
                    synced_count += 1
                
            except Exception as e:
                logger.error(f"Error syncing calendar event {event.get('id')}: {e}", exc_info=True)
                continue
        
        logger.info(f"Successfully synced {synced_count} episodes from Google Calendar")
        return synced_count
        
    except HttpError as e:
        logger.error(f"Google Calendar API error during sync: {e}", exc_info=True)
        return 0
    except Exception as e:
        logger.error(f"Unexpected error during calendar sync: {e}", exc_info=True)
        return 0
