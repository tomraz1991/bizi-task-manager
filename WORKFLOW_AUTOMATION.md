# Workflow Automation Implementation

## Overview

This document describes the automatic workflow system that creates and manages tasks based on episode recording schedules and status changes.

## Features

### 1. Daily Workflow Automation

- **Google Calendar Integration**: Every morning, the system queries Google Calendar for today's episodes
- **Studio Preparation Tasks**: Automatically creates studio preparation tasks for each episode scheduled today
- **Task Assignment**: Tasks are assigned to the recording engineer for that episode
- **Due Date**: Tasks are due 1 hour before the recording time

### 2. Automatic Task Creation

Tasks are automatically created based on episode status:

- **Studio Preparation**: Created when episode is scheduled for today (via daily workflow)
- **Editing Task**: Created when episode status changes to "recorded"
- **Reels Task**: Created when episode status changes to "recorded"
- **Publishing Task**: Created when both editing and reels are approved by the client

### 3. Task Completion Logic

#### Studio Preparation Task

- Automatically marked as done when:
  - Episode status changes to "recorded", OR
  - Task is manually marked as done

#### Editing Task

- Only marked as done when:
  - Client approval status is set to "approved"
- If client rejects, task is reset to "in_progress"

#### Reels Task

- Only marked as done when:
  - Client approval status is set to "approved"
- If client rejects, task is reset to "in_progress"

#### Publishing Task

- Created automatically when both editing and reels are approved
- Can be manually completed

## Database Changes

### New Fields

#### Podcast Table

- `default_studio_settings` (TEXT): Default studio setup for the podcast (e.g., "two mics, two cameras one in front of the other")

#### Episode Table

- `studio_settings_override` (TEXT): Override default studio settings for special episodes (e.g., "3 mics" for guest episodes)
- `client_approved_editing` (TEXT): Client approval status for editing ("pending", "approved", "rejected")
- `client_approved_reels` (TEXT): Client approval status for reels ("pending", "approved", "rejected")

### New Task Type

- `STUDIO_PREPARATION`: Task for preparing the studio before recording

## Migration

Run the migration script to add the new database fields:

```bash
cd backend
./venv/bin/python migrate_workflow_fields.py
```

## API Endpoints

### Workflow Endpoints

#### POST `/api/workflow/daily`

Manually trigger the daily workflow process. This endpoint:

- Queries Google Calendar for today's episodes
- Creates studio preparation tasks for each episode

**Response:**

```json
{
  "message": "Daily workflow processed successfully",
  "episodes_processed": 3
}
```

## Google Calendar Integration

Currently, the Google Calendar integration queries the database for episodes with `recording_date` set to today.

**TODO for Production:**

1. Implement actual Google Calendar API integration
2. Authenticate with Google Calendar API
3. Query calendar events for today
4. Match events to episodes (by podcast name, episode number, etc.)
5. Create episodes if they don't exist in database

The placeholder implementation is in `backend/services/google_calendar.py`.

## UI Changes

### Episode Modal

- **Studio Settings Section**:
  - Shows default studio settings from the podcast (read-only)
  - Allows overriding settings for special episodes
- **Client Approvals Section** (shown when episode status is "sent_to_client" or "in_editing"):
  - Editing approval dropdown (Pending/Approved/Rejected)
  - Reels approval dropdown (Pending/Approved/Rejected)

### Podcast Management

- Podcasts can now have a `default_studio_settings` field that can be set when creating or updating a podcast

## Workflow Flow

1. **Morning (Daily Workflow)**:

   - System queries Google Calendar for today's episodes
   - Creates studio preparation tasks for each episode
   - Tasks are due 1 hour before recording time

2. **After Recording**:

   - When episode status changes to "recorded":
     - Studio preparation task is auto-completed
     - Editing task is created (due 2 days after recording)
     - Reels task is created (due 2 days after recording)

3. **Client Review**:

   - When episode is sent to client:
     - Client can approve/reject editing
     - Client can approve/reject reels
     - Tasks are updated based on approval status

4. **Publishing**:
   - When both editing and reels are approved:
     - Publishing task is automatically created
     - Episode is ready for publishing

## Setting Up Daily Workflow

### Option 1: Manual Trigger

Call the API endpoint manually:

```bash
curl -X POST http://localhost:8000/api/workflow/daily
```

### Option 2: Scheduled Job (Recommended)

Set up a cron job or scheduled task to call the endpoint daily:

**Cron Example:**

```bash
# Run every day at 8 AM
0 8 * * * curl -X POST http://localhost:8000/api/workflow/daily
```

**Python Script Example:**

```python
import schedule
import time
import requests

def run_daily_workflow():
    response = requests.post('http://localhost:8000/api/workflow/daily')
    print(f"Workflow result: {response.json()}")

schedule.every().day.at("08:00").do(run_daily_workflow)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Testing

1. **Test Studio Preparation Task Creation**:

   - Create an episode with `recording_date` set to today
   - Call `/api/workflow/daily`
   - Verify studio preparation task is created

2. **Test Task Auto-Completion**:

   - Mark episode status as "recorded"
   - Verify studio preparation task is marked as done
   - Verify editing and reels tasks are created

3. **Test Client Approval**:
   - Set episode status to "sent_to_client"
   - Set `client_approved_editing` to "approved"
   - Verify editing task is marked as done
   - Set `client_approved_reels` to "approved"
   - Verify reels task is marked as done
   - Verify publishing task is created

## Notes

- Studio preparation tasks disappear from the table when:
  - Episode status is "recorded", OR
  - Task is manually marked as done
- Editing and reels tasks require client approval to be marked as done
- Publishing task is only created when both editing and reels are approved
- The system handles task creation idempotently (won't create duplicate tasks)
