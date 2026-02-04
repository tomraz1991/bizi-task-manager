"""
Episode API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import nullslast, func
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Episode, EpisodeStatus
from schemas import Episode as EpisodeSchema, EpisodeCreate, EpisodeUpdate, EpisodeWithPodcast
from constants import DEFAULT_NOTIFICATION_DAYS

router = APIRouter()


@router.get("/", response_model=List[EpisodeWithPodcast])
async def get_episodes(
    skip: int = Query(0, ge=0, description="Number of episodes to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of episodes to return"),
    podcast_id: Optional[str] = None,
    status: Optional[EpisodeStatus] = None,
    date_from: Optional[datetime] = Query(None, description="Filter episodes from this date (inclusive)"),
    date_to: Optional[datetime] = Query(None, description="Filter episodes to this date (inclusive)"),
    db: Session = Depends(get_db)
):
    """Get all episodes with optional filtering and pagination."""
    # Use eager loading to load podcast and engineer relationships
    query = db.query(Episode).options(
        joinedload(Episode.podcast),
        joinedload(Episode.recording_engineer),
        joinedload(Episode.editing_engineer),
        joinedload(Episode.reels_engineer)
    )
    
    if podcast_id:
        query = query.filter(Episode.podcast_id == podcast_id)
    if status:
        query = query.filter(Episode.status == status)
    if date_from:
        query = query.filter(Episode.recording_date >= date_from)
    if date_to:
        query = query.filter(Episode.recording_date <= date_to)
    
    # Handle null recording_date by putting nulls last
    episodes = query.order_by(nullslast(Episode.recording_date.desc())).offset(skip).limit(limit).all()
    return episodes


@router.get("/count", response_model=dict)
async def get_episodes_count(
    podcast_id: Optional[str] = None,
    status: Optional[EpisodeStatus] = None,
    date_from: Optional[datetime] = Query(None, description="Filter episodes from this date (inclusive)"),
    date_to: Optional[datetime] = Query(None, description="Filter episodes to this date (inclusive)"),
    db: Session = Depends(get_db)
):
    """Get total count of episodes matching the filters."""
    from sqlalchemy import func
    
    query = db.query(func.count(Episode.id))
    
    if podcast_id:
        query = query.filter(Episode.podcast_id == podcast_id)
    if status:
        query = query.filter(Episode.status == status)
    if date_from:
        query = query.filter(Episode.recording_date >= date_from)
    if date_to:
        query = query.filter(Episode.recording_date <= date_to)
    
    total = query.scalar() or 0
    return {"total": total}


@router.get("/{episode_id}", response_model=EpisodeWithPodcast)
async def get_episode(episode_id: str, db: Session = Depends(get_db)):
    """Get a specific episode."""
    episode = db.query(Episode).options(
        joinedload(Episode.podcast),
        joinedload(Episode.recording_engineer),
        joinedload(Episode.editing_engineer),
        joinedload(Episode.reels_engineer)
    ).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode


@router.post("/", response_model=EpisodeSchema)
async def create_episode(episode: EpisodeCreate, db: Session = Depends(get_db)):
    """Create a new episode."""
    # Validate podcast exists
    from models import Podcast, User
    podcast = db.query(Podcast).filter(Podcast.id == episode.podcast_id).first()
    if not podcast:
        raise HTTPException(status_code=400, detail=f"Podcast with id {episode.podcast_id} not found")
    
    # Validate engineers exist if provided
    if episode.recording_engineer_id:
        user = db.query(User).filter(User.id == episode.recording_engineer_id).first()
        if not user:
            raise HTTPException(status_code=400, detail=f"Recording engineer with id {episode.recording_engineer_id} not found")
    
    if episode.editing_engineer_id:
        user = db.query(User).filter(User.id == episode.editing_engineer_id).first()
        if not user:
            raise HTTPException(status_code=400, detail=f"Editing engineer with id {episode.editing_engineer_id} not found")
    
    if episode.reels_engineer_id:
        user = db.query(User).filter(User.id == episode.reels_engineer_id).first()
        if not user:
            raise HTTPException(status_code=400, detail=f"Reels engineer with id {episode.reels_engineer_id} not found")
    
    db_episode = Episode(**episode.model_dump())
    db.add(db_episode)
    db.commit()
    db.refresh(db_episode)
    return db_episode


@router.put("/{episode_id}", response_model=EpisodeSchema)
async def update_episode(
    episode_id: str, episode_update: EpisodeUpdate, db: Session = Depends(get_db)
):
    """Update an episode."""
    db_episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not db_episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    # Track old status for workflow automation
    old_status = db_episode.status
    
    update_data = episode_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_episode, field, value)
    
    db.commit()
    db.refresh(db_episode)
    
    # Trigger workflow automation if status or client approvals changed
    if old_status != db_episode.status or 'client_approved_editing' in update_data or 'client_approved_reels' in update_data:
        from services.workflow_automation import process_episode_status_change
        try:
            process_episode_status_change(db, db_episode, old_status)
        except Exception as e:
            # Log error but don't fail the update
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in workflow automation: {e}", exc_info=True)
    
    return db_episode


@router.delete("/{episode_id}")
async def delete_episode(episode_id: str, db: Session = Depends(get_db)):
    """Delete an episode."""
    db_episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not db_episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    db.delete(db_episode)
    db.commit()
    return {"message": "Episode deleted successfully"}


@router.get("/upcoming/recordings", response_model=List[EpisodeWithPodcast])
async def get_upcoming_recordings(
    days_ahead: int = Query(DEFAULT_NOTIFICATION_DAYS, description="Number of days ahead to look"),
    db: Session = Depends(get_db)
):
    """Get upcoming recording sessions."""
    from datetime import timedelta, timezone
    now = datetime.now(timezone.utc)
    future_date = now + timedelta(days=days_ahead)
    
    episodes = db.query(Episode).options(
        joinedload(Episode.podcast),
        joinedload(Episode.recording_engineer),
        joinedload(Episode.editing_engineer),
        joinedload(Episode.reels_engineer)
    ).filter(
        Episode.recording_date >= now,
        Episode.recording_date <= future_date
    ).order_by(Episode.recording_date.asc()).all()
    
    return episodes
