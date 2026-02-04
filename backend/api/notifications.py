"""
Notifications API endpoints.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime, timedelta

from database import get_db
from models import Episode, Task, TaskStatus
from schemas import NotificationItem
from constants import DEFAULT_NOTIFICATION_DAYS, FAR_FUTURE_DAYS, TASK_TYPE_LABELS

router = APIRouter()


@router.get("/", response_model=List[NotificationItem])
async def get_notifications(
    days_ahead: int = Query(DEFAULT_NOTIFICATION_DAYS, description="Number of days ahead to look"),
    db: Session = Depends(get_db)
):
    """Get all notifications for upcoming recordings and due tasks."""
    from datetime import timezone
    notifications = []
    now = datetime.now(timezone.utc)
    # Make now naive for comparison with naive episode dates
    now_naive = now.replace(tzinfo=None)
    future_date = now_naive + timedelta(days=days_ahead)
    
    # Get upcoming recording sessions with eager loading
    upcoming_episodes = db.query(Episode).options(
        joinedload(Episode.podcast),
        joinedload(Episode.recording_engineer),
        joinedload(Episode.editing_engineer),
        joinedload(Episode.reels_engineer)
    ).filter(
        Episode.recording_date >= now_naive,
        Episode.recording_date <= future_date
    ).order_by(Episode.recording_date.asc()).all()
    
    for episode in upcoming_episodes:
        if not episode.recording_date:
            continue  # Skip episodes without recording dates
            
        days_until = (episode.recording_date - now_naive).days
        priority = "urgent" if days_until <= 1 else ("high" if days_until <= 3 else "normal")
        
        # Convert naive datetime to aware for NotificationItem
        recording_date_aware = episode.recording_date
        if recording_date_aware and recording_date_aware.tzinfo is None:
            # Assume UTC for naive datetimes
            from datetime import timezone
            recording_date_aware = recording_date_aware.replace(tzinfo=timezone.utc)
        
        notifications.append(NotificationItem(
            id=f"recording_{episode.id}",
            type="recording_session",
            title=f"Recording Session: {episode.podcast.name if episode.podcast else 'Unknown Podcast'}",
            message=f"Episode {episode.episode_number or 'N/A'} scheduled for {episode.recording_date.strftime('%Y-%m-%d %H:%M')}",
            due_date=recording_date_aware,
            episode_id=episode.id,
            priority=priority
        ))
    
    # Get due tasks with eager loading
    # Tasks may have timezone-aware dates, so use the timezone-aware now
    due_tasks = db.query(Task).options(
        joinedload(Task.episode).joinedload(Episode.podcast),
        joinedload(Task.assigned_user)
    ).filter(
        Task.due_date >= now,
        Task.due_date <= now + timedelta(days=days_ahead),
        Task.status != TaskStatus.DONE,
        Task.status != TaskStatus.SKIPPED
    ).order_by(Task.due_date.asc()).all()
    
    for task in due_tasks:
        if not task.due_date:
            continue  # Skip tasks without due dates
        
        # Handle both naive and aware datetimes
        if task.due_date.tzinfo is None:
            days_until = (task.due_date - now_naive).days
        else:
            days_until = (task.due_date - now).days
        priority = "urgent" if days_until <= 1 else ("high" if days_until <= 3 else "normal")
        
        episode_name = task.episode.podcast.name if task.episode and task.episode.podcast else "Unknown"
        
        # Ensure due_date is timezone-aware
        due_date_aware = task.due_date
        if due_date_aware and due_date_aware.tzinfo is None:
            from datetime import timezone
            due_date_aware = due_date_aware.replace(tzinfo=timezone.utc)
        
        notifications.append(NotificationItem(
            id=f"task_{task.id}",
            type="due_task",
            title=f"{TASK_TYPE_LABELS.get(task.type, task.type.title())} Task Due",
            message=f"{TASK_TYPE_LABELS.get(task.type, task.type.title())} for {episode_name} - Episode {task.episode.episode_number if task.episode else 'N/A'}",
            due_date=due_date_aware,
            episode_id=task.episode_id,
            task_id=task.id,
            priority=priority
        ))
    
    # Get overdue tasks with eager loading
    # Tasks may have timezone-aware dates, so use the timezone-aware now
    overdue_tasks = db.query(Task).options(
        joinedload(Task.episode).joinedload(Episode.podcast),
        joinedload(Task.assigned_user)
    ).filter(
        Task.due_date < now,
        Task.status != TaskStatus.DONE,
        Task.status != TaskStatus.SKIPPED
    ).order_by(Task.due_date.asc()).all()
    
    for task in overdue_tasks:
        if not task.due_date:
            continue  # Skip tasks without due dates
            
        episode_name = task.episode.podcast.name if task.episode and task.episode.podcast else "Unknown"
        
        # Ensure due_date is timezone-aware
        due_date_aware = task.due_date
        if due_date_aware and due_date_aware.tzinfo is None:
            from datetime import timezone
            due_date_aware = due_date_aware.replace(tzinfo=timezone.utc)
        
        notifications.append(NotificationItem(
            id=f"overdue_task_{task.id}",
            type="due_task",
            title=f"OVERDUE: {TASK_TYPE_LABELS.get(task.type, task.type.title())} Task",
            message=f"{TASK_TYPE_LABELS.get(task.type, task.type.title())} for {episode_name} - Episode {task.episode.episode_number if task.episode else 'N/A'}",
            due_date=due_date_aware,
            episode_id=task.episode_id,
            task_id=task.id,
            priority="urgent"
        ))
    
    # Sort by due date
    notifications.sort(key=lambda x: x.due_date)
    
    return notifications
