"""
Database models for Podcast Task Manager.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from enum import Enum

from database import Base


def utcnow():
    """Get current UTC datetime (replacement for deprecated datetime.utcnow())."""
    return datetime.now(timezone.utc)


class EpisodeStatus(str, Enum):
    """Episode status values."""
    NOT_STARTED = "not_started"
    RECORDED = "recorded"
    IN_EDITING = "in_editing"
    SENT_TO_CLIENT = "sent_to_client"
    PUBLISHED = "published"


class TaskType(str, Enum):
    """Task type values."""
    RECORDING = "recording"
    EDITING = "editing"
    REELS = "reels"
    PUBLISHING = "publishing"
    STUDIO_PREPARATION = "studio_preparation"


class TaskStatus(str, Enum):
    """Task status values."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    SENT_TO_CLIENT = "sent_to_client"  # Editing/reels: work done, awaiting client approval
    DONE = "done"
    SKIPPED = "skipped"


class PodcastAlias(Base):
    """Alternative name for a podcast (e.g. for matching Google Calendar event titles)."""
    __tablename__ = "podcast_aliases"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    podcast_id = Column(String, ForeignKey("podcasts.id", ondelete="CASCADE"), nullable=False, index=True)
    alias = Column(String, nullable=False, unique=True, index=True)

    podcast = relationship("Podcast", back_populates="aliases")


class Podcast(Base):
    """Podcast model."""
    __tablename__ = "podcasts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    host = Column(String, nullable=True)
    default_studio_settings = Column(Text, nullable=True)  # Default studio setup (e.g., "two mics, two cameras one in front of the other")
    tasks_time_allowance_days = Column(String, nullable=True)  # How long engineers have to complete all tasks (e.g. "7", "3 days", "1 week")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    episodes = relationship("Episode", back_populates="podcast", cascade="all, delete-orphan")
    aliases = relationship("PodcastAlias", back_populates="podcast", cascade="all, delete-orphan")


class Episode(Base):
    """Episode model."""
    __tablename__ = "episodes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    podcast_id = Column(String, ForeignKey("podcasts.id"), nullable=False, index=True)
    episode_number = Column(String, nullable=True)
    recording_date = Column(DateTime, nullable=True, index=True)
    studio = Column(String, nullable=True)
    guest_names = Column(Text, nullable=True)
    status = Column(SQLEnum(EpisodeStatus), default=EpisodeStatus.NOT_STARTED, index=True)
    episode_notes = Column(Text, nullable=True)
    drive_link = Column(String, nullable=True)
    backup_deletion_date = Column(DateTime, nullable=True)
    card_name = Column(String, nullable=True, index=True)
    memory_card = Column(String, nullable=True)  # Which memory card stores recordings (e.g. "kingstone 1", "WD 500G")
    recording_engineer_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    editing_engineer_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    reels_engineer_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    reels_notes = Column(Text, nullable=True)
    studio_settings_override = Column(Text, nullable=True)  # Override default studio settings for this episode
    client_approved_editing = Column(String, default="pending")  # "pending", "approved", "rejected"
    client_approved_reels = Column(String, default="pending")  # "pending", "approved", "rejected"
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    podcast = relationship("Podcast", back_populates="episodes")
    recording_engineer = relationship("User", foreign_keys=[recording_engineer_id], backref="episodes_as_recording_engineer")
    editing_engineer = relationship("User", foreign_keys=[editing_engineer_id], backref="episodes_as_editing_engineer")
    reels_engineer = relationship("User", foreign_keys=[reels_engineer_id], backref="episodes_as_reels_engineer")
    tasks = relationship("Task", back_populates="episode", cascade="all, delete-orphan")


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True, index=True)
    email = Column(String, nullable=True)
    role = Column(String, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships are defined via foreign_keys in Episode and Task models


class Task(Base):
    """Task model."""
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    episode_id = Column(String, ForeignKey("episodes.id"), nullable=False, index=True)
    type = Column(SQLEnum(TaskType), nullable=False, index=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.NOT_STARTED, index=True)
    assigned_to = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    due_date = Column(DateTime, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    episode = relationship("Episode", back_populates="tasks")
    assigned_user = relationship("User", foreign_keys=[assigned_to], backref="assigned_tasks")
