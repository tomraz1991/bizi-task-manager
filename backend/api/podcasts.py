"""
Podcast API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from database import get_db
from models import Podcast, PodcastAlias
from schemas import Podcast as PodcastSchema, PodcastCreate, PodcastUpdate, PodcastAliasCreate, PodcastAliasOut

router = APIRouter()


@router.get("/", response_model=List[PodcastSchema])
async def get_podcasts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all podcasts with aliases."""
    podcasts = db.query(Podcast).options(joinedload(Podcast.aliases)).offset(skip).limit(limit).all()
    return podcasts


@router.get("/{podcast_id}", response_model=PodcastSchema)
async def get_podcast(podcast_id: str, db: Session = Depends(get_db)):
    """Get a specific podcast with aliases."""
    podcast = db.query(Podcast).options(joinedload(Podcast.aliases)).filter(Podcast.id == podcast_id).first()
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")
    return podcast


@router.post("/", response_model=PodcastSchema)
async def create_podcast(podcast: PodcastCreate, db: Session = Depends(get_db)):
    """Create a new podcast, optionally with aliases."""
    data = podcast.model_dump(exclude={"aliases"})
    db_podcast = Podcast(**data)
    db.add(db_podcast)
    db.commit()
    db.refresh(db_podcast)
    # Create alias records if provided
    aliases = podcast.aliases or []
    for raw in aliases:
        alias_str = (raw or "").strip()
        if not alias_str:
            continue
        existing = db.query(PodcastAlias).filter(PodcastAlias.alias == alias_str).first()
        if existing:
            continue  # skip if already used by another podcast
        db.add(PodcastAlias(podcast_id=db_podcast.id, alias=alias_str))
    db.commit()
    # Return podcast with aliases loaded
    db.refresh(db_podcast)
    db_podcast = db.query(Podcast).options(joinedload(Podcast.aliases)).filter(Podcast.id == db_podcast.id).first()
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


# --- Aliases ---

@router.get("/{podcast_id}/aliases", response_model=List[PodcastAliasOut])
async def get_podcast_aliases(podcast_id: str, db: Session = Depends(get_db)):
    """List aliases for a podcast."""
    podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")
    return db.query(PodcastAlias).filter(PodcastAlias.podcast_id == podcast_id).all()


@router.post("/{podcast_id}/aliases", response_model=PodcastAliasOut)
async def add_podcast_alias(
    podcast_id: str, body: PodcastAliasCreate, db: Session = Depends(get_db)
):
    """Add an alias for a podcast (e.g. for matching Google Calendar event titles)."""
    podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")
    alias_str = (body.alias or "").strip()
    if not alias_str:
        raise HTTPException(status_code=400, detail="Alias cannot be empty")
    existing = db.query(PodcastAlias).filter(PodcastAlias.alias == alias_str).first()
    if existing:
        if existing.podcast_id == podcast_id:
            return existing
        raise HTTPException(status_code=400, detail="This alias is already used by another podcast")
    alias_row = PodcastAlias(podcast_id=podcast_id, alias=alias_str)
    db.add(alias_row)
    db.commit()
    db.refresh(alias_row)
    return alias_row


@router.delete("/{podcast_id}/aliases/{alias_id}")
async def delete_podcast_alias(
    podcast_id: str, alias_id: str, db: Session = Depends(get_db)
):
    """Remove an alias from a podcast."""
    alias_row = db.query(PodcastAlias).filter(
        PodcastAlias.id == alias_id,
        PodcastAlias.podcast_id == podcast_id,
    ).first()
    if not alias_row:
        raise HTTPException(status_code=404, detail="Alias not found")
    db.delete(alias_row)
    db.commit()
    return {"message": "Alias deleted"}
