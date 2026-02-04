# Google Calendar Integration - Implementation Summary

## ✅ What Was Implemented

### 1. Dependencies Added
- `google-api-python-client==2.108.0`
- `google-auth-httplib2==0.1.1`
- `google-auth-oauthlib==1.1.0`

### 2. Configuration System
- Created `backend/config.py` with `Settings` class using `pydantic-settings`
- Reads from `.env` file automatically
- All Google Calendar settings configurable via environment variables

### 3. Full Google Calendar Integration
- **Authentication**: Service account authentication
- **Event Fetching**: Queries Google Calendar for today's events
- **Event Parsing**: Extracts podcast name, episode number, date, studio, guests from events
- **Episode Matching**: Matches calendar events to existing episodes or creates new ones
- **Podcast Creation**: Automatically creates podcasts if they don't exist
- **Fallback**: Gracefully falls back to database query if calendar is disabled/unavailable

### 4. Features
- **Flexible Title Parsing**: Supports multiple event title formats:
  - `רוני וברק - פרק 33`
  - `Recording: רוני וברק #33`
  - `רוני וברק פרק 33`
- **Extended Properties Support**: Can read episode metadata from calendar event extended properties
- **Guest Extraction**: Parses guest names from event description
- **Studio Detection**: Extracts studio from event location
- **Timezone Support**: Configurable timezone for calendar events

### 5. API Endpoints
- `POST /api/workflow/daily` - Triggers daily workflow (fetches today's episodes)
- `POST /api/workflow/sync-calendar?days_ahead=7` - Syncs calendar events to database

### 6. Documentation
- `GOOGLE_CALENDAR_SETUP.md` - Complete setup guide
- `GOOGLE_CALENDAR_INTEGRATION.md` - Technical details
- `.env.example` - Configuration template

## 📋 Next Steps

### 1. Install Dependencies
```bash
cd backend
./venv/bin/pip install -r requirements.txt
```

### 2. Set Up Google Cloud
1. Create Google Cloud project
2. Enable Google Calendar API
3. Create Service Account
4. Download credentials JSON file

### 3. Configure Environment
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your settings
```

### 4. Share Calendar
- Share your Google Calendar with the service account email
- Grant "See all event details" permission

### 5. Test
```bash
# Test calendar sync
curl -X POST http://localhost:8000/api/workflow/sync-calendar

# Test daily workflow
curl -X POST http://localhost:8000/api/workflow/daily
```

## 🔧 Configuration Options

All settings in `backend/.env`:

- `GOOGLE_CALENDAR_ENABLED` - Enable/disable calendar integration
- `GOOGLE_CALENDAR_ID` - Calendar ID (default: "primary")
- `GOOGLE_CREDENTIALS_PATH` - Path to service account JSON
- `GOOGLE_CALENDAR_TIMEZONE` - Timezone for events (default: Asia/Jerusalem)
- `GOOGLE_CALENDAR_LOOKAHEAD_DAYS` - Days ahead to sync (default: 7)

## 🎯 How It Works

1. **Daily Workflow** (`/api/workflow/daily`):
   - Fetches today's events from Google Calendar
   - Parses events to extract episode data
   - Creates/updates episodes in database
   - Creates studio preparation tasks for each episode

2. **Calendar Sync** (`/api/workflow/sync-calendar`):
   - Fetches upcoming events (configurable days ahead)
   - Creates/updates episodes in database
   - Useful for initial sync or periodic updates

3. **Event Parsing**:
   - Extracts podcast name and episode number from title
   - Gets recording date from event start time
   - Extracts studio from location
   - Parses guests from description
   - Supports extended properties for structured data

4. **Episode Matching**:
   - Matches by podcast name, episode number, and date
   - Updates existing episodes if found
   - Creates new episodes if not found
   - Creates podcasts automatically if they don't exist

## 🛡️ Error Handling

- Gracefully falls back to database query if calendar is unavailable
- Logs all errors for debugging
- Continues processing other events if one fails
- Handles missing credentials gracefully

## 📝 Notes

- The system works even if Google Calendar is disabled (falls back to database)
- All calendar operations are logged for debugging
- Service account authentication is used (no user interaction required)
- Calendar must be shared with service account email
