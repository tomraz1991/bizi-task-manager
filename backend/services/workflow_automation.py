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


def _task_notes_with_episode(base: str, episode: Episode) -> str:
    """Append episode notes to task notes when present."""
    if episode.episode_notes and episode.episode_notes.strip():
        return f"{base}\n\nEpisode notes: {episode.episode_notes.strip()}"
    return base


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
    
    base_notes = f"Studio setup: {studio_settings}" if studio_settings else "Prepare studio for recording"
    task = Task(
        episode_id=episode.id,
        type=TaskType.STUDIO_PREPARATION,
        status=TaskStatus.NOT_STARTED,
        assigned_to=episode.recording_engineer_id,  # Assign to recording engineer
        due_date=due_date,
        notes=_task_notes_with_episode(base_notes, episode)
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    logger.info(f"Created studio preparation task {task.id} for episode {episode.id}")
    return task


def create_recording_task(db: Session, episode: Episode) -> Optional[Task]:
    """Create a recording task for an episode if it doesn't exist (e.g. after studio prep is done)."""
    existing = db.query(Task).filter(
        and_(
            Task.episode_id == episode.id,
            Task.type == TaskType.RECORDING
        )
    ).first()
    if existing:
        return existing
    due_date = None
    if episode.recording_date:
        due_date = episode.recording_date
        now_utc = datetime.now(timezone.utc)
        now_compare = now_utc.replace(tzinfo=None) if (due_date.tzinfo is None) else now_utc
        if due_date < now_compare:
            due_date = now_utc.replace(tzinfo=None) if (due_date.tzinfo is None) else now_utc
    task = Task(
        episode_id=episode.id,
        type=TaskType.RECORDING,
        status=TaskStatus.NOT_STARTED,
        assigned_to=episode.recording_engineer_id,
        due_date=due_date,
        notes=_task_notes_with_episode("Record the episode", episode)
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    logger.info(f"Created recording task {task.id} for episode {episode.id}")
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
    
    base_notes = "Edit episode. Update to 'Sent to client' when sent; complete when client approves."
    task = Task(
        episode_id=episode.id,
        type=TaskType.EDITING,
        status=TaskStatus.NOT_STARTED,
        assigned_to=episode.editing_engineer_id,
        due_date=due_date,
        notes=_task_notes_with_episode(base_notes, episode)
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
    
    base_notes = episode.reels_notes or "Export reels from episode. Update to 'Sent to client' when sent; complete when client approves."
    task = Task(
        episode_id=episode.id,
        type=TaskType.REELS,
        status=TaskStatus.NOT_STARTED,
        assigned_to=episode.reels_engineer_id,
        due_date=due_date,
        notes=_task_notes_with_episode(base_notes, episode)
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
        base_notes = "Publish episode. Both editing and reels have been approved by client."
        task = Task(
            episode_id=episode.id,
            type=TaskType.PUBLISHING,
            status=TaskStatus.NOT_STARTED,
            assigned_to=None,  # Can be assigned later
            due_date=None,
            notes=_task_notes_with_episode(base_notes, episode)
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
            # Reset to in_progress if client rejected (was done or sent to client)
            if task.status in (TaskStatus.DONE, TaskStatus.SENT_TO_CLIENT):
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
            # Reset to in_progress if client rejected (was done or sent to client)
            if task.status in (TaskStatus.DONE, TaskStatus.SENT_TO_CLIENT):
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


def process_task_status_change(db: Session, task: Task, old_status: TaskStatus):
    """Process workflow when a task is updated (e.g. studio prep done -> recording task; recording done -> episode recorded)."""
    if old_status == TaskStatus.DONE:
        return  # no transition to DONE
    if task.status != TaskStatus.DONE:
        return

    episode = db.query(Episode).filter(Episode.id == task.episode_id).first()
    if not episode:
        return

    if task.type == TaskType.STUDIO_PREPARATION:
        create_recording_task(db, episode)
        logger.info(f"Studio preparation task {task.id} marked done -> created recording task for episode {episode.id}")
    elif task.type == TaskType.RECORDING:
        old_episode_status = episode.status
        episode.status = EpisodeStatus.RECORDED
        db.commit()
        db.refresh(episode)
        process_episode_status_change(db, episode, old_episode_status)
        logger.info(f"Recording task {task.id} marked done -> episode {episode.id} status set to recorded")


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
