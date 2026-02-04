"""
Engineer/Team Member API endpoints for viewing assignments.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from database import get_db
from models import Episode, User, EpisodeStatus, Task
from schemas import EpisodeWithPodcast

router = APIRouter()


@router.get("/{engineer_id}/episodes", response_model=List[EpisodeWithPodcast])
async def get_engineer_episodes(
    engineer_id: str,
    role: Optional[str] = Query(None, description="Filter by role: recording, editing, or reels"),
    status: Optional[EpisodeStatus] = None,
    upcoming_only: bool = Query(False, description="Only show upcoming recordings"),
    days_ahead: int = Query(30, description="Days ahead for upcoming filter"),
    db: Session = Depends(get_db)
):
    """
    Get all episodes assigned to a specific engineer.
    Can filter by role (recording, editing, reels) and status.
    """
    from sqlalchemy.orm import joinedload
    
    query = db.query(Episode).options(
        joinedload(Episode.podcast),
        joinedload(Episode.recording_engineer),
        joinedload(Episode.editing_engineer),
        joinedload(Episode.reels_engineer)
    )
    
    # Filter by engineer role
    if role == "recording":
        query = query.filter(Episode.recording_engineer_id == engineer_id)
    elif role == "editing":
        query = query.filter(Episode.editing_engineer_id == engineer_id)
    elif role == "reels":
        query = query.filter(Episode.reels_engineer_id == engineer_id)
    else:
        # Show all roles
        query = query.filter(
            or_(
                Episode.recording_engineer_id == engineer_id,
                Episode.editing_engineer_id == engineer_id,
                Episode.reels_engineer_id == engineer_id
            )
        )
    
    # Filter by status
    if status:
        query = query.filter(Episode.status == status)
    
    # Filter upcoming recordings
    if upcoming_only:
        now = datetime.now(timezone.utc)
        future_date = now + timedelta(days=days_ahead)
        query = query.filter(
            Episode.recording_date >= now,
            Episode.recording_date <= future_date
        )
    
    episodes = query.order_by(Episode.recording_date.desc()).all()
    return episodes


@router.get("/{engineer_id}/upcoming", response_model=List[EpisodeWithPodcast])
async def get_engineer_upcoming(
    engineer_id: str,
    days_ahead: int = Query(7, description="Number of days ahead to look"),
    db: Session = Depends(get_db)
):
    """Get upcoming recording sessions for a specific engineer."""
    from sqlalchemy.orm import joinedload
    from datetime import timedelta, timezone
    
    now = datetime.now(timezone.utc)
    future_date = now + timedelta(days=days_ahead)
    
    episodes = db.query(Episode).options(
        joinedload(Episode.podcast),
        joinedload(Episode.recording_engineer),
        joinedload(Episode.editing_engineer),
        joinedload(Episode.reels_engineer)
    ).filter(
        Episode.recording_engineer_id == engineer_id,
        Episode.recording_date >= now,
        Episode.recording_date <= future_date
    ).order_by(Episode.recording_date.asc()).all()
    
    return episodes


@router.get("/{engineer_id}/tasks")
async def get_engineer_tasks(
    engineer_id: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all tasks assigned to an engineer.
    Includes both episode-level assignments and additional tasks.
    """
    from models import Task, TaskStatus
    from sqlalchemy.orm import joinedload
    
    # Get tasks from Task table
    task_query = db.query(Task).options(
        joinedload(Task.episode).joinedload(Episode.podcast),
        joinedload(Task.assigned_user)
    ).filter(Task.assigned_to == engineer_id)
    
    if status:
        task_query = task_query.filter(Task.status == TaskStatus[status.upper()])
    
    tasks = task_query.all()
    
    # Also get episodes where engineer is assigned (as episode-level assignments)
    episodes = db.query(Episode).options(
        joinedload(Episode.podcast),
        joinedload(Episode.recording_engineer),
        joinedload(Episode.editing_engineer),
        joinedload(Episode.reels_engineer)
    ).filter(
        or_(
            Episode.recording_engineer_id == engineer_id,
            Episode.editing_engineer_id == engineer_id,
            Episode.reels_engineer_id == engineer_id
        )
    ).all()
    
    # Format response
    result = []
    
    # Add tasks
    for task in tasks:
        result.append({
            "type": "task",
            "id": task.id,
            "episode_id": task.episode_id,
            "task_type": task.type,
            "status": task.status,
            "due_date": task.due_date,
            "notes": task.notes,
            "episode": {
                "id": task.episode.id if task.episode else None,
                "podcast": task.episode.podcast.name if task.episode and task.episode.podcast else None,
                "episode_number": task.episode.episode_number if task.episode else None,
            }
        })
    
    # Add episode assignments
    for episode in episodes:
        roles = []
        if episode.recording_engineer_id == engineer_id:
            roles.append("recording")
        if episode.editing_engineer_id == engineer_id:
            roles.append("editing")
        if episode.reels_engineer_id == engineer_id:
            roles.append("reels")
        
        for role in roles:
            result.append({
                "type": "episode_assignment",
                "id": f"{episode.id}_{role}",
                "episode_id": episode.id,
                "task_type": role,
                "status": episode.status,
                "recording_date": episode.recording_date,
                "notes": episode.reels_notes if role == "reels" else episode.episode_notes,
                "episode": {
                    "id": episode.id,
                    "podcast": episode.podcast.name if episode.podcast else None,
                    "episode_number": episode.episode_number,
                }
            })
    
    return result


@router.get("/")
async def get_all_engineers_summary(db: Session = Depends(get_db)):
    """Get summary of all engineers with their assignment counts."""
    from sqlalchemy import func
    
    users = db.query(User).all()
    result = []
    
    for user in users:
        recording_count = db.query(func.count(Episode.id)).filter(
            Episode.recording_engineer_id == user.id
        ).scalar() or 0
        
        editing_count = db.query(func.count(Episode.id)).filter(
            Episode.editing_engineer_id == user.id
        ).scalar() or 0
        
        reels_count = db.query(func.count(Episode.id)).filter(
            Episode.reels_engineer_id == user.id
        ).scalar() or 0
        
        from models import Task
        task_count = db.query(func.count(Task.id)).filter(
            Task.assigned_to == user.id
        ).scalar() or 0
        
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "assignments": {
                "recording_episodes": recording_count,
                "editing_episodes": editing_count,
                "reels_episodes": reels_count,
                "additional_tasks": task_count,
                "total": recording_count + editing_count + reels_count + task_count
            }
        })
    
    return result
