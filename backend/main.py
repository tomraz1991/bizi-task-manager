"""
FastAPI application for Podcast Task Manager.
"""
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api import podcasts, episodes, tasks, users, notifications, import_csv, engineers, workflow
from database import init_db

app = FastAPI(
    title="Podcast Task Manager API",
    description="Task management system for recording studio",
    version="1.0.0"
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# CORS middleware for frontend
from config import settings

_raw = (settings.CORS_ORIGINS or "").strip()
if _raw == "*" or not _raw:
    # Allow all origins when unset or explicitly "*" (credentials must be False with "*")
    CORS_ORIGINS = ["*"]
    CORS_CREDENTIALS = False
else:
    CORS_ORIGINS = [o.strip() for o in _raw.split(",") if o.strip()]
    CORS_CREDENTIALS = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include routers
app.include_router(podcasts.router, prefix="/api/podcasts", tags=["podcasts"])
app.include_router(episodes.router, prefix="/api/episodes", tags=["episodes"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(import_csv.router, prefix="/api/import", tags=["import"])
app.include_router(engineers.router, prefix="/api/engineers", tags=["engineers"])
app.include_router(workflow.router, prefix="/api/workflow", tags=["workflow"])


@app.get("/")
async def root():
    return {"message": "Podcast Task Manager API", "version": "1.0.0"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
