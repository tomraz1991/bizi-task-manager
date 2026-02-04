"""
Workflow automation API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from services.workflow_automation import process_daily_workflow
from services.google_calendar import sync_calendar_to_database

router = APIRouter()


@router.post("/daily")
async def trigger_daily_workflow(db: Session = Depends(get_db)):
    """
    Manually trigger the daily workflow process.
    
    This endpoint:
    1. Queries Google Calendar for today's episodes
    2. Creates studio preparation tasks for each episode
    """
    try:
        count = process_daily_workflow(db)
        return {
            "message": "Daily workflow processed successfully",
            "episodes_processed": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing workflow: {str(e)}")


@router.post("/sync-calendar")
async def sync_calendar(
    days_ahead: Optional[int] = Query(None, description="Number of days ahead to sync"),
    db: Session = Depends(get_db)
):
    """
    Sync Google Calendar events to database episodes.
    
    This endpoint:
    1. Queries Google Calendar for upcoming events
    2. Creates or updates episodes in database
    3. Returns count of synced episodes
    """
    try:
        count = sync_calendar_to_database(db, days_ahead)
        return {
            "message": "Calendar sync completed successfully",
            "episodes_synced": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing calendar: {str(e)}")
