"""
CSV import API endpoint.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import csv
import io
from datetime import datetime
import logging

from database import get_db
from models import Podcast, Episode, Task, User, EpisodeStatus, TaskType, TaskStatus
from utils import parse_date
from constants import MAX_CSV_FILE_SIZE

router = APIRouter()
logger = logging.getLogger(__name__)


def get_or_create_user(db: Session, name: str) -> Optional[User]:
    """Get existing user or create new one."""
    if not name or name.strip() == "":
        return None
    
    name = name.strip()
    user = db.query(User).filter(User.name == name).first()
    if not user:
        user = User(name=name)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_csv_value(row: dict, *keys) -> str:
    """Get value from CSV row, trying multiple key variations (with/without trailing spaces)."""
    for key in keys:
        # Try exact key
        value = row.get(key, "")
        if value:
            return value
        # Try with trailing space
        value = row.get(key + " ", "")
        if value:
            return value
        # Try without trailing space (if key had one)
        if key.endswith(" "):
            value = row.get(key.rstrip(), "")
            if value:
                return value
    return ""


def get_or_create_podcast(db: Session, name: str, host: Optional[str] = None) -> Optional[Podcast]:
    """Get existing podcast or create new one."""
    if not name or name.strip() == "":
        return None
    
    name = name.strip()
    podcast = db.query(Podcast).filter(Podcast.name == name).first()
    if not podcast:
        podcast = Podcast(name=name, host=host)
        db.add(podcast)
        db.commit()
        db.refresh(podcast)
    return podcast


def parse_episode_status(status_str: str) -> EpisodeStatus:
    """Parse Hebrew status to EpisodeStatus enum."""
    if not status_str:
        return EpisodeStatus.NOT_STARTED
    
    status_str = status_str.strip()
    status_map = {
        "הוקלט": EpisodeStatus.RECORDED,
        "בעריכה": EpisodeStatus.IN_EDITING,
        "הופץ": EpisodeStatus.PUBLISHED,
        "נשלח ללקוח": EpisodeStatus.SENT_TO_CLIENT,
        "לא התחילה": EpisodeStatus.NOT_STARTED,
    }
    
    return status_map.get(status_str, EpisodeStatus.NOT_STARTED)


@router.post("/csv")
async def import_csv_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Import episodes and tasks from CSV file.
    Expected CSV format matches the Hebrew CSV structure.
    """
    # Validate file
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    # Check file size
    contents = await file.read()
    if len(contents) > MAX_CSV_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
    
    try:
        text = contents.decode('utf-8-sig')  # Handle BOM
        csv_reader = csv.DictReader(io.StringIO(text))
        
        imported_count = 0
        errors = []
        
        # Use transaction for atomicity
        try:
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    # Extract data from CSV row
                    # Note: First column (empty key) contains host name in some rows
                    podcast_name = row.get("שם הפודקאסט", "").strip()
                    # Get first column value (host name) - check all possible keys
                    host_name = ""
                    for key in row.keys():
                        if not key or key.strip() == "":
                            host_name = row.get(key, "").strip()
                            break
                    if not host_name:
                        # Try getting by index if DictReader preserves order
                        values = list(row.values())
                        if values and not values[0].startswith("שם הפודקאסט"):
                            host_name = values[0].strip() if values[0] else ""
                    recording_date_str = row.get("תאריך הקלטה", "").strip()
                    studio = row.get("אולפן", "").strip()
                    episode_number = row.get("פרק מספר", "").strip()
                    guest_names = row.get("שם אורחים", "").strip()
                    status_str = row.get("סטטוס", "").strip()
                    episode_notes = get_csv_value(row, "הערות לפרק").strip()
                    card_name = get_csv_value(row, "על איזה כרטיס").strip()
                    # Handle trailing spaces in CSV headers
                    recording_person = get_csv_value(row, "הקלטה").strip()
                    editing_person = get_csv_value(row, "עריכה").strip()
                    reels_person = get_csv_value(row, "reels").strip()
                    reels_notes = get_csv_value(row, "הערות לרילס").strip()
                    drive_link = get_csv_value(row, "לינק לדרייב").strip()
                    backup_deletion_date_str = get_csv_value(row, "ת. מחיקה מגיבוי").strip()
                    
                    # Skip empty rows
                    if not podcast_name:
                        continue
                    
                    # Get or create podcast
                    podcast = get_or_create_podcast(db, podcast_name, host_name)
                    if not podcast:
                        errors.append(f"Row {row_num}: Could not create podcast")
                        continue
                    
                    # Parse dates
                    recording_date = parse_date(recording_date_str)
                    backup_deletion_date = parse_date(backup_deletion_date_str)
                    
                    # Debug: Log date parsing for first few rows
                    if row_num <= 5 and recording_date:
                        logger.info(f"Row {row_num}: Parsed '{recording_date_str}' as {recording_date} (year: {recording_date.year})")
                    
                    # Parse status
                    status = parse_episode_status(status_str)
                    
                    # Get or create engineers and assign to episode
                    recording_engineer_id = None
                    editing_engineer_id = None
                    reels_engineer_id = None
                    
                    if recording_person:
                        recording_user = get_or_create_user(db, recording_person)
                        if recording_user:
                            recording_engineer_id = recording_user.id
                    
                    if editing_person:
                        editing_user = get_or_create_user(db, editing_person)
                        if editing_user:
                            editing_engineer_id = editing_user.id
                    
                    if reels_person:
                        reels_user = get_or_create_user(db, reels_person)
                        if reels_user:
                            reels_engineer_id = reels_user.id
                    
                    # Create episode with engineer assignments
                    episode = Episode(
                        podcast_id=podcast.id,
                        episode_number=episode_number if episode_number else None,
                        recording_date=recording_date,
                        studio=studio if studio else None,
                        guest_names=guest_names if guest_names else None,
                        status=status,
                        episode_notes=episode_notes if episode_notes else None,
                        drive_link=drive_link if drive_link else None,
                        backup_deletion_date=backup_deletion_date,
                        card_name=card_name if card_name else None,
                        recording_engineer_id=recording_engineer_id,
                        editing_engineer_id=editing_engineer_id,
                        reels_engineer_id=reels_engineer_id,
                        reels_notes=reels_notes if reels_notes else None,
                    )
                    db.add(episode)
                    db.flush()  # Get episode ID
                    
                    # Debug: Verify stored date
                    if row_num <= 5 and recording_date:
                        logger.info(f"Row {row_num}: Stored recording_date as {episode.recording_date} (year: {episode.recording_date.year if episode.recording_date else None})")
                    
                    imported_count += 1
                    
                except Exception as e:
                    error_msg = f"Row {row_num}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg, exc_info=True)
                    # Rollback this row's transaction to allow processing to continue
                    try:
                        db.rollback()
                    except:
                        pass  # Ignore rollback errors
                    continue
            
            db.commit()
            
            return {
                "message": f"Successfully imported {imported_count} episodes",
                "imported_count": imported_count,
                "errors": errors if errors else None
            }
        except Exception as e:
            # Rollback on error
            db.rollback()
            logger.error(f"Transaction failed during CSV import: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error importing CSV: {str(e)}. All changes have been rolled back."
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during CSV import: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Error importing CSV: {str(e)}")
