"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, field_serializer
from typing import Optional, List, Any
from datetime import datetime
from models import EpisodeStatus, TaskType, TaskStatus


class PodcastBase(BaseModel):
    name: str
    host: Optional[str] = None
    default_studio_settings: Optional[str] = None
    tasks_time_allowance_days: Optional[str] = None  # e.g. "7", "3 days", "1 week"


class PodcastCreate(PodcastBase):
    aliases: Optional[List[str]] = None  # Optional aliases when creating (e.g. for Google Calendar matching)


class PodcastUpdate(BaseModel):
    name: Optional[str] = None
    host: Optional[str] = None
    default_studio_settings: Optional[str] = None
    tasks_time_allowance_days: Optional[str] = None


class Podcast(PodcastBase):
    id: str
    created_at: datetime
    updated_at: datetime
    aliases: Optional[List[Any]] = None  # From relationship: list of PodcastAlias or list of str

    class Config:
        from_attributes = True

    @field_serializer("aliases")
    def serialize_aliases(self, v):
        if v is None:
            return []
        return [a.alias if hasattr(a, "alias") else a for a in v]


class PodcastAliasCreate(BaseModel):
    alias: str


class PodcastAliasOut(BaseModel):
    id: str
    podcast_id: str
    alias: str

    class Config:
        from_attributes = True


class EpisodeBase(BaseModel):
    podcast_id: str
    episode_number: Optional[str] = None
    recording_date: Optional[datetime] = None
    studio: Optional[str] = None
    guest_names: Optional[str] = None
    status: EpisodeStatus = EpisodeStatus.NOT_STARTED
    episode_notes: Optional[str] = None
    drive_link: Optional[str] = None
    backup_deletion_date: Optional[datetime] = None
    card_name: Optional[str] = None
    memory_card: Optional[str] = None
    recording_engineer_id: Optional[str] = None
    editing_engineer_id: Optional[str] = None
    reels_engineer_id: Optional[str] = None
    reels_notes: Optional[str] = None
    studio_settings_override: Optional[str] = None
    client_approved_editing: Optional[str] = "pending"
    client_approved_reels: Optional[str] = "pending"


class EpisodeCreate(EpisodeBase):
    pass


class EpisodeUpdate(BaseModel):
    podcast_id: Optional[str] = None
    episode_number: Optional[str] = None
    recording_date: Optional[datetime] = None
    studio: Optional[str] = None
    guest_names: Optional[str] = None
    status: Optional[EpisodeStatus] = None
    episode_notes: Optional[str] = None
    drive_link: Optional[str] = None
    backup_deletion_date: Optional[datetime] = None
    card_name: Optional[str] = None
    memory_card: Optional[str] = None
    recording_engineer_id: Optional[str] = None
    editing_engineer_id: Optional[str] = None
    reels_engineer_id: Optional[str] = None
    reels_notes: Optional[str] = None
    studio_settings_override: Optional[str] = None
    client_approved_editing: Optional[str] = None
    client_approved_reels: Optional[str] = None


class Episode(EpisodeBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    name: str
    email: Optional[str] = None
    role: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EpisodeWithPodcast(Episode):
    podcast: Optional[Podcast] = None
    recording_engineer: Optional[User] = None
    editing_engineer: Optional[User] = None
    reels_engineer: Optional[User] = None

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    episode_id: str
    type: TaskType
    status: TaskStatus = TaskStatus.NOT_STARTED
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    episode_id: Optional[str] = None
    type: Optional[TaskType] = None
    status: Optional[TaskStatus] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None


class Task(TaskBase):
    id: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskWithEpisode(Task):
    episode: Optional[EpisodeWithPodcast] = None
    assigned_user: Optional[User] = None

    class Config:
        from_attributes = True


class NotificationItem(BaseModel):
    id: str
    type: str  # "recording_session" or "due_task"
    title: str
    message: str
    due_date: datetime
    episode_id: Optional[str] = None
    task_id: Optional[str] = None
    priority: str = "normal"  # "low", "normal", "high", "urgent"

    class Config:
        from_attributes = True
