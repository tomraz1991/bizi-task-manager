"""
User API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User
from schemas import User as UserSchema, UserCreate, UserUpdate

router = APIRouter()


@router.get("/", response_model=List[UserSchema])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get a specific user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserSchema)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    # Check if user with same name already exists
    existing = db.query(User).filter(User.name == user.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this name already exists")
    
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: str, user_update: UserUpdate, db: Session = Depends(get_db)
):
    """Update a user."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Check name uniqueness if name is being updated
    if "name" in update_data:
        existing = db.query(User).filter(
            User.name == update_data["name"],
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="User with this name already exists")
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}")
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    """
    Delete a user.
    
    Note: This will set owner_id to NULL for all tasks assigned to this user.
    Consider reassigning tasks before deletion.
    """
    from models import Task
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user has assigned tasks or episode assignments
    from models import Task, Episode
    task_count = db.query(Task).filter(Task.assigned_to == user_id).count()
    episode_count = db.query(Episode).filter(
        (Episode.recording_engineer_id == user_id) |
        (Episode.editing_engineer_id == user_id) |
        (Episode.reels_engineer_id == user_id)
    ).count()
    
    if task_count > 0 or episode_count > 0:
        # Set assigned_to to None for all tasks (cascade behavior)
        db.query(Task).filter(Task.assigned_to == user_id).update({Task.assigned_to: None})
        # Set engineer fields to None for all episodes
        db.query(Episode).filter(Episode.recording_engineer_id == user_id).update({Episode.recording_engineer_id: None})
        db.query(Episode).filter(Episode.editing_engineer_id == user_id).update({Episode.editing_engineer_id: None})
        db.query(Episode).filter(Episode.reels_engineer_id == user_id).update({Episode.reels_engineer_id: None})
        # Option 2: Could raise an error instead:
        # raise HTTPException(
        #     status_code=400,
        #     detail=f"Cannot delete user: {task_count} task(s) are assigned to this user. Please reassign tasks first."
        # )
    
    db.delete(db_user)
    db.commit()
    return {
        "message": "User deleted successfully",
        "tasks_unassigned": task_count,
        "episodes_unassigned": episode_count
    }
