"""
Configuration management using environment variables.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Database
    DATABASE_URL: str = "sqlite:///./podcast_task_manager.db"
    
    # Google Calendar Configuration
    GOOGLE_CALENDAR_ENABLED: bool = False
    GOOGLE_CALENDAR_ID: str = "primary"
    GOOGLE_CREDENTIALS_PATH: Optional[str] = None
    GOOGLE_SERVICE_ACCOUNT_EMAIL: Optional[str] = None
    GOOGLE_CALENDAR_TIMEZONE: str = "Asia/Jerusalem"
    GOOGLE_CALENDAR_LOOKAHEAD_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
