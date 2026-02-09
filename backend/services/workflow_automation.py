"""
Workflow automation service for automatic task creation and management.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models import Episode, Task, Podcast, EpisodeStatus, TaskType, TaskStatus
from services.google_calendar import get_todays_episodes_from_calendar

logger = logging.getLogger(__name__)


def create_studio_preparation_task(db: Session, episode: Episode) -> Optional[Task]:
    """Create a studio preparation task for an episode if it doesn't exist."""
    # Check if task already exists
    existing = db.query(Task).filter(
        and_(
            Task.episode_id == episode.id,
            Task.type == TaskType.STUDIO_PREPARATION
        )
    ).first()
    
    if existing:
        return existing
    
    # Get studio settings (episode override or podcast default)
    studio_settings = episode.studio_settings_override or (episode.podcast.default_studio_settings if episode.podcast else None)
    
    # Create task due before recording time (1 hour before)
    due_date = None
    if episode.recording_date:
        due_date = episode.recording_date - timedelta(hours=1)
        # If due date is in the past, set to now (use naive UTC to match DB datetimes)
        now_utc = datetime.now(timezone.utc)
        now_compare = now_utc.replace(tzinfo=None) if (due_date.tzinfo is None) else now_utc
        if due_date < now_compare:
            due_date = now_utc.replace(tzinfo=None) if (due_date.tzinfo is None) else now_utc
    
    task = Task(
        episode_id=episode.id,
        type=TaskType.STUDIO_PREPARATION,
        status=TaskStatus.NOT_STARTED,
        assigned_to=episode.recording_engineer_id,  # Assign to recording engineer
        due_date=due_date,
        notes=f"Studio setup: {studio_settings}" if studio_settings else "Prepare studio for recording"
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    logger.info(f"Created studio preparation task {task.id} for episode {episode.id}")
    return task


def create_editing_task(db: Session, episode: Episode) -> Optional[Task]:
    """Create an editing task for an episode if it doesn't exist."""
    # Check if task already exists
    existing = db.query(Task).filter(
        and_(
            Task.episode_id == episode.id,
            Task.type == TaskType.EDITING
        )
    ).first()
    
    if existing:
        return existing
    
    # Create task due 2 days after recording
    due_date = None
    if episode.recording_date:
        due_date = episode.recording_date + timedelta(days=2)
    
    task = Task(
        episode_id=episode.id,
        type=TaskType.EDITING,
        status=TaskStatus.NOT_STARTED,
        assigned_to=episode.editing_engineer_id,
        due_date=due_date,
        notes="Edit episode. Task will be marked complete when client approves."
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    logger.info(f"Created editing task {task.id} for episode {episode.id}")
    return task


def create_reels_task(db: Session, episode: Episode) -> Optional[Task]:
    """Create a reels task for an episode if it doesn't exist."""
    # Check if task already exists
    existing = db.query(Task).filter(
        and_(
            Task.episode_id == episode.id,
            Task.type == TaskType.REELS
        )
    ).first()
    
    if existing:
        return existing
    
    # Create task due 2 days after recording
    due_date = None
    if episode.recording_date:
        due_date = episode.recording_date + timedelta(days=2)
    
    task = Task(
        episode_id=episode.id,
        type=TaskType.REELS,
        status=TaskStatus.NOT_STARTED,
        assigned_to=episode.reels_engineer_id,
        due_date=due_date,
        notes=episode.reels_notes or "Export reels from episode. Task will be marked complete when client approves."
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    logger.info(f"Created reels task {task.id} for episode {episode.id}")
    return task


def create_publishing_task(db: Session, episode: Episode) -> Optional[Task]:
    """Create a publishing task when both editing and reels are approved."""
    # Check if task already exists
    existing = db.query(Task).filter(
        and_(
            Task.episode_id == episode.id,
            Task.type == TaskType.PUBLISHING
        )
    ).first()
    
    if existing:
        return existing
    
    # Only create if both are approved
    if episode.client_approved_editing == "approved" and episode.client_approved_reels == "approved":
        task = Task(
            episode_id=episode.id,
            type=TaskType.PUBLISHING,
            status=TaskStatus.NOT_STARTED,
            assigned_to=None,  # Can be assigned later
            due_date=None,
            notes="Publish episode. Both editing and reels have been approved by client."
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        logger.info(f"Created publishing task {task.id} for episode {episode.id}")
        return task
    
    return None


def auto_complete_studio_preparation(db: Session, episode: Episode):
    """Auto-complete studio preparation task when episode is recorded."""
    task = db.query(Task).filter(
        and_(
            Task.episode_id == episode.id,
            Task.type == TaskType.STUDIO_PREPARATION,
            Task.status != TaskStatus.DONE
        )
    ).first()
    
    if task:
        task.status = TaskStatus.DONE
        task.completed_at = datetime.now(timezone.utc)
        db.commit()
        logger.info(f"Auto-completed studio preparation task {task.id} for episode {episode.id}")


def sync_editing_task_status(db: Session, episode: Episode):
    """Update editing task status based on client approval."""
    task = db.query(Task).filter(
        and_(
            Task.episode_id == episode.id,
            Task.type == TaskType.EDITING
        )
    ).first()
    
    if task:
        if episode.client_approved_editing == "approved":
            if task.status != TaskStatus.DONE:
                task.status = TaskStatus.DONE
                task.completed_at = datetime.now(timezone.utc)
                db.commit()
                logger.info(f"Marked editing task {task.id} as done (client approved)")
        elif episode.client_approved_editing == "rejected":
            # Reset to in_progress if client rejected
            if task.status == TaskStatus.DONE:
                task.status = TaskStatus.IN_PROGRESS
                task.completed_at = None
                db.commit()
                logger.info(f"Reset editing task {task.id} to in_progress (client rejected)")


def sync_reels_task_status(db: Session, episode: Episode):
    """Update reels task status based on client approval."""
    task = db.query(Task).filter(
        and_(
            Task.episode_id == episode.id,
            Task.type == TaskType.REELS
        )
    ).first()
    
    if task:
        if episode.client_approved_reels == "approved":
            if task.status != TaskStatus.DONE:
                task.status = TaskStatus.DONE
                task.completed_at = datetime.now(timezone.utc)
                db.commit()
                logger.info(f"Marked reels task {task.id} as done (client approved)")
        elif episode.client_approved_reels == "rejected":
            # Reset to in_progress if client rejected
            if task.status == TaskStatus.DONE:
                task.status = TaskStatus.IN_PROGRESS
                task.completed_at = None
                db.commit()
                logger.info(f"Reset reels task {task.id} to in_progress (client rejected)")


def delete_stale_studio_preparation_tasks(db: Session) -> int:
    """Delete studio preparation tasks that are more than 1 day overdue. Returns count deleted."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=1)
    # Normalize for DB comparison (due_date may be stored naive UTC)
    cutoff_naive = cutoff.replace(tzinfo=None) if cutoff.tzinfo else cutoff
    deleted = db.query(Task).filter(
        and_(
            Task.type == TaskType.STUDIO_PREPARATION,
            Task.due_date.is_not(None),
            Task.due_date < cutoff_naive
        )
    ).delete(synchronize_session=False)
    if deleted:
        db.commit()
        logger.info(f"Deleted {deleted} stale studio preparation task(s) (> 1 day overdue)")
    return deleted


def process_daily_workflow(db: Session):
    """Process daily workflow: create tasks for today's episodes from Google Calendar."""
    logger.info("Starting daily workflow processing")
    
    try:
        # Remove studio preparation tasks that are more than 1 day overdue
        delete_stale_studio_preparation_tasks(db)
        
        # Get today's episodes from Google Calendar
        today_episodes = get_todays_episodes_from_calendar(db)
        
        logger.info(f"Found {len(today_episodes)} episodes scheduled for today")
        
        for episode in today_episodes:
            # Create studio preparation task
            create_studio_preparation_task(db, episode)
            
        logger.info("Daily workflow processing completed")
        return len(today_episodes)
    except Exception as e:
        logger.error(f"Error in daily workflow processing: {e}", exc_info=True)
        raise


def process_episode_status_change(db: Session, episode: Episode, old_status: EpisodeStatus):
    """Process workflow changes when episode status changes."""
    logger.info(f"Processing status change for episode {episode.id}: {old_status} -> {episode.status}")
    
    # If episode is now recorded, auto-complete studio preparation
    if episode.status == EpisodeStatus.RECORDED:
        auto_complete_studio_preparation(db, episode)
        
        # Create editing and reels tasks if they don't exist
        create_editing_task(db, episode)
        create_reels_task(db, episode)
    
    # Sync task statuses based on client approvals
    sync_editing_task_status(db, episode)
    sync_reels_task_status(db, episode)
    
    # Create publishing task if both are approved
    create_publishing_task(db, episode)
