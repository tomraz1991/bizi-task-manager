# Google Calendar Integration Requirements

## Overview

This document outlines what's needed to implement full Google Calendar integration for automatic episode discovery and task creation.

## What's Currently Implemented

- ✅ Placeholder function that queries database for today's episodes
- ✅ Workflow automation that creates tasks based on episodes
- ✅ Database structure ready for calendar-synced episodes

## What's Missing for Full Implementation

### 1. Python Dependencies

Add to `backend/requirements.txt`:

```txt
google-api-python-client==2.108.0
google-auth-httplib2==0.1.1
google-auth-oauthlib==1.1.0
```

Install with:

```bash
cd backend
./venv/bin/pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 2. Google Cloud Setup

#### A. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable **Google Calendar API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

#### B. Create OAuth 2.0 Credentials

Choose one authentication method:

**Option 1: Service Account (Recommended for Server-to-Server)**

- Best for automated background jobs
- No user interaction required
- Navigate to "APIs & Services" > "Credentials"
- Click "Create Credentials" > "Service Account"
- Download JSON key file
- Share calendar with service account email

**Option 2: OAuth 2.0 Client ID (For User Authorization)**

- Best if you need to access user's personal calendar
- Requires user consent flow
- Navigate to "APIs & Services" > "Credentials"
- Click "Create Credentials" > "OAuth 2.0 Client ID"
- Configure consent screen
- Download credentials JSON

### 3. Environment Variables

Add to `.env` or environment:

```bash
# Google Calendar Configuration
GOOGLE_CALENDAR_ID=primary  # or specific calendar ID
GOOGLE_CREDENTIALS_PATH=./credentials/google-credentials.json
GOOGLE_SERVICE_ACCOUNT_EMAIL=your-service-account@project.iam.gserviceaccount.com

# Optional: Calendar-specific settings
GOOGLE_CALENDAR_TIMEZONE=Asia/Jerusalem  # or your timezone
GOOGLE_CALENDAR_LOOKAHEAD_DAYS=7  # How many days ahead to sync
```

### 4. Calendar Event Matching Strategy

**Decision Needed:** How are episodes identified in calendar events?

Possible approaches:

#### Option A: Event Title Pattern Matching

- Parse event title for podcast name and episode number
- Example: "רוני וברק - פרק 33" → Podcast: "רוני וברק", Episode: "33"
- Requires consistent naming convention in calendar

#### Option B: Event Description/Extended Properties

- Store episode ID or podcast ID in event description or extended properties
- More reliable but requires calendar events to be created with this metadata
- Example: `episode_id: abc-123` in description

#### Option C: Custom Event Fields

- Use Google Calendar's extended properties to store:
  - `podcast_id`
  - `episode_number`
  - `studio`
  - `guest_names`
- Most reliable but requires calendar events to be structured

**Recommendation:** Start with Option A (title parsing) with fallback to Option B (description), then migrate to Option C for new events.

### 5. Event Data Extraction

Need to extract from calendar events:

- **Podcast Name**: From title or description
- **Episode Number**: From title or description
- **Recording Date/Time**: From event start time
- **Studio**: From location or description
- **Guest Names**: From description or attendees
- **Engineers**: From attendees or description
- **Notes**: From description

### 6. Implementation Details Needed

#### A. Authentication Function

```python
def get_calendar_service():
    """Authenticate and return Google Calendar service object."""
    # Service account or OAuth flow
    pass
```

#### B. Event Query Function

```python
def get_todays_events(service, calendar_id: str) -> List[Event]:
    """Query Google Calendar for today's events."""
    # Use Calendar API to fetch events
    pass
```

#### C. Event Parsing Function

```python
def parse_event_to_episode(event: Event, db: Session) -> Optional[Episode]:
    """Parse calendar event and create/update episode in database."""
    # Extract podcast name, episode number, etc.
    # Match to existing podcast or create new
    # Create or update episode
    pass
```

#### D. Podcast Name Matching

- How to match calendar event podcast name to database podcast?
- Exact match? Fuzzy match? Create new if not found?
- Handle Hebrew vs transliterated names?

### 7. Configuration Questions

**Please provide:**

1. **Calendar ID**: Which Google Calendar should we read from?

   - Primary calendar?
   - Shared calendar?
   - Multiple calendars?

2. **Event Naming Convention**: How are episodes named in calendar?

   - Format examples: "רוני וברק - פרק 33", "Recording: רוני וברק #33", etc.
   - Is there a consistent pattern?

3. **Timezone**: What timezone are recording times in?

   - Calendar timezone?
   - Studio location timezone?
   - UTC?

4. **Event Frequency**: How often should we sync?

   - Daily (morning)?
   - Real-time (webhook)?
   - On-demand (API call)?

5. **Error Handling**: What should happen if:
   - Calendar event doesn't match any podcast?
   - Multiple podcasts match the same name?
   - Episode already exists in database?

### 8. Additional Features (Optional)

- **Bidirectional Sync**: Update calendar when episode recording_date changes
- **Webhook Integration**: Real-time updates when calendar events change
- **Multiple Calendar Support**: Read from multiple calendars
- **Event Creation**: Create calendar events when episodes are created
- **Conflict Resolution**: Handle calendar updates vs database updates

## Implementation Steps

Once you provide the information above, I can implement:

1. ✅ Add dependencies to requirements.txt
2. ✅ Create authentication module
3. ✅ Implement calendar event fetching
4. ✅ Implement event parsing and matching
5. ✅ Create episode creation/update logic
6. ✅ Add error handling and logging
7. ✅ Update workflow automation to use real calendar
8. ✅ Add configuration management
9. ✅ Add tests

## Quick Start (Minimal Implementation)

If you want a basic implementation now, I can create it with these assumptions:

- Service account authentication
- Read from primary calendar
- Parse podcast name and episode number from event title
- Create episodes if podcast exists, skip if not found
- Use event start time as recording_date

**Would you like me to:**

1. Implement the basic version with assumptions?
2. Wait for you to provide the configuration details?
3. Create a configurable version that you can customize?

## Security Considerations

- Store credentials securely (not in git)
- Use service account with minimal permissions
- Rotate credentials regularly
- Log access for audit purposes
- Handle token expiration gracefully

## Testing

Will need:

- Test Google Calendar with sample events
- Test authentication flow
- Test event parsing with various formats
- Test episode matching and creation
- Test error scenarios
