"""
Podcast API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Podcast
from schemas import Podcast as PodcastSchema, PodcastCreate, PodcastUpdate

router = APIRouter()


@router.get("/", response_model=List[PodcastSchema])
async def get_podcasts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all podcasts."""
    podcasts = db.query(Podcast).offset(skip).limit(limit).all()
    return podcasts


@router.get("/{podcast_id}", response_model=PodcastSchema)
async def get_podcast(podcast_id: str, db: Session = Depends(get_db)):
    """Get a specific podcast."""
    podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")
    return podcast


@router.post("/", response_model=PodcastSchema)
async def create_podcast(podcast: PodcastCreate, db: Session = Depends(get_db)):
    """Create a new podcast."""
    db_podcast = Podcast(**podcast.model_dump())
    db.add(db_podcast)
    db.commit()
    db.refresh(db_podcast)
    return db_podcast


@router.put("/{podcast_id}", response_model=PodcastSchema)
async def update_podcast(
    podcast_id: str, podcast_update: PodcastUpdate, db: Session = Depends(get_db)
):
    """Update a podcast."""
    db_podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
    if not db_podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")
    
    update_data = podcast_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_podcast, field, value)
    
    db.commit()
    db.refresh(db_podcast)
    return db_podcast


@router.delete("/{podcast_id}")
async def delete_podcast(podcast_id: str, db: Session = Depends(get_db)):
    """Delete a podcast."""
    db_podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
    if not db_podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")
    
    db.delete(db_podcast)
    db.commit()
    return {"message": "Podcast deleted successfully"}
