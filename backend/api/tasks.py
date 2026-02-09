"""
Task API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import nullslast, or_
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from database import get_db
from models import Task, TaskStatus, TaskType, Episode
from schemas import Task as TaskSchema, TaskCreate, TaskUpdate, TaskWithEpisode
from constants import DEFAULT_NOTIFICATION_DAYS

router = APIRouter()

# Studio preparation tasks more than 1 day overdue are excluded from lists and cleaned up daily
def _exclude_stale_studio_prep_filter():
    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=1)).replace(tzinfo=None)  # naive UTC for DB comparison
    return or_(
        Task.type != TaskType.STUDIO_PREPARATION,
        Task.due_date.is_(None),
        Task.due_date >= cutoff
    )


@router.get("/", response_model=List[TaskWithEpisode])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    episode_id: Optional[str] = None,
    assigned_to: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    task_type: Optional[TaskType] = None,
    db: Session = Depends(get_db)
):
    """Get all tasks with optional filtering. Studio preparation tasks > 1 day overdue are excluded."""
    # Use eager loading to prevent N+1 queries
    query = db.query(Task).options(
        joinedload(Task.episode).joinedload(Episode.podcast),
        joinedload(Task.assigned_user)
    ).filter(_exclude_stale_studio_prep_filter())
    
    if episode_id:
        query = query.filter(Task.episode_id == episode_id)
    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)
    if status:
        query = query.filter(Task.status == status)
    if task_type:
        query = query.filter(Task.type == task_type)
    
    # Handle null due_date by putting nulls last
    tasks = query.order_by(nullslast(Task.due_date.asc())).offset(skip).limit(limit).all()
    return tasks


@router.get("/{task_id}", response_model=TaskWithEpisode)
async def get_task(task_id: str, db: Session = Depends(get_db)):
    """Get a specific task."""
    task = db.query(Task).options(
        joinedload(Task.episode).joinedload(Episode.podcast),
        joinedload(Task.assigned_user)
    ).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/", response_model=TaskSchema)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task."""
    # Validate episode exists
    from models import Episode
    episode = db.query(Episode).filter(Episode.id == task.episode_id).first()
    if not episode:
        raise HTTPException(status_code=400, detail=f"Episode with id {task.episode_id} not found")
    
    # Validate assigned user exists if provided
    if task.assigned_to:
        from models import User
        user = db.query(User).filter(User.id == task.assigned_to).first()
        if not user:
            raise HTTPException(status_code=400, detail=f"User with id {task.assigned_to} not found")
    
    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.put("/{task_id}", response_model=TaskSchema)
async def update_task(
    task_id: str, task_update: TaskUpdate, db: Session = Depends(get_db)
):
    """Update a task."""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.model_dump(exclude_unset=True)
    
    # Auto-set completed_at when status changes to DONE
    if update_data.get("status") == TaskStatus.DONE and db_task.status != TaskStatus.DONE:
        from datetime import timezone
        update_data["completed_at"] = datetime.now(timezone.utc)
    elif update_data.get("status") != TaskStatus.DONE and db_task.status == TaskStatus.DONE:
        update_data["completed_at"] = None
    
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task


@router.delete("/{task_id}")
async def delete_task(task_id: str, db: Session = Depends(get_db)):
    """Delete a task."""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}


@router.get("/due/upcoming", response_model=List[TaskWithEpisode])
async def get_due_tasks(
    days_ahead: int = Query(DEFAULT_NOTIFICATION_DAYS, description="Number of days ahead to look"),
    db: Session = Depends(get_db)
):
    """Get tasks that are due soon. Studio preparation tasks > 1 day overdue are excluded."""
    now = datetime.now(timezone.utc)
    future_date = now + timedelta(days=days_ahead)
    
    tasks = db.query(Task).options(
        joinedload(Task.episode).joinedload(Episode.podcast),
        joinedload(Task.assigned_user)
    ).filter(
        _exclude_stale_studio_prep_filter(),
        Task.due_date >= now,
        Task.due_date <= future_date,
        Task.status != TaskStatus.DONE,
        Task.status != TaskStatus.SKIPPED
    ).order_by(Task.due_date.asc()).all()
    
    return tasks


@router.get("/overdue", response_model=List[TaskWithEpisode])
async def get_overdue_tasks(db: Session = Depends(get_db)):
    """Get overdue tasks. Studio preparation tasks > 1 day overdue are excluded (and removed from DB by daily workflow)."""
    now = datetime.now(timezone.utc)
    
    tasks = db.query(Task).options(
        joinedload(Task.episode).joinedload(Episode.podcast),
        joinedload(Task.assigned_user)
    ).filter(
        _exclude_stale_studio_prep_filter(),
        Task.due_date < now,
        Task.status != TaskStatus.DONE,
        Task.status != TaskStatus.SKIPPED
    ).order_by(Task.due_date.asc()).all()
    
    return tasks
