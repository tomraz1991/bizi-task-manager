# Google Calendar Setup Guide

## Quick Start

1. **Install dependencies:**
   ```bash
   cd backend
   ./venv/bin/pip install -r requirements.txt
   ```

2. **Set up Google Cloud credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project or select existing
   - Enable Google Calendar API
   - Create Service Account credentials
   - Download JSON key file

3. **Configure environment:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your settings
   ```

4. **Set up calendar sharing:**
   - Share your Google Calendar with the service account email
   - Grant "See all event details" permission

## Detailed Setup

### Step 1: Google Cloud Project Setup

1. **Create/Select Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing

2. **Enable Google Calendar API:**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

### Step 2: Create Service Account

1. **Navigate to Credentials:**
   - Go to "APIs & Services" > "Credentials"

2. **Create Service Account:**
   - Click "Create Credentials" > "Service Account"
   - Enter name: "podcast-task-manager"
   - Click "Create and Continue"
   - Skip role assignment (optional)
   - Click "Done"

3. **Create Key:**
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Select "JSON" format
   - Download the file

4. **Save Credentials:**
   - Move downloaded JSON file to `backend/credentials/google-service-account.json`
   - **Important:** Add `credentials/` to `.gitignore` to avoid committing secrets

### Step 3: Share Calendar

1. **Get Service Account Email:**
   - Open the downloaded JSON file
   - Find `"client_email"` field
   - Copy the email address (e.g., `podcast-task-manager@project-id.iam.gserviceaccount.com`)

2. **Share Calendar:**
   - Open Google Calendar
   - Go to calendar settings
   - Under "Share with specific people", click "Add people"
   - Enter the service account email
   - Select permission: "See all event details"
   - Click "Send"

### Step 4: Configure Environment

1. **Copy example file:**
   ```bash
   cp backend/.env.example backend/.env
   ```

2. **Edit `.env` file:**
   ```bash
   # Enable Google Calendar
   GOOGLE_CALENDAR_ENABLED=true
   
   # Calendar ID (use "primary" for main calendar)
   GOOGLE_CALENDAR_ID=primary
   
   # Path to credentials file
   GOOGLE_CREDENTIALS_PATH=./credentials/google-service-account.json
   
   # Timezone
   GOOGLE_CALENDAR_TIMEZONE=Asia/Jerusalem
   ```

3. **Create credentials directory:**
   ```bash
   mkdir -p backend/credentials
   # Add credentials/.gitignore
   echo "*" > backend/credentials/.gitignore
   echo "!.gitignore" >> backend/credentials/.gitignore
   ```

### Step 5: Test Integration

1. **Test calendar sync:**
   ```bash
   curl -X POST http://localhost:8000/api/workflow/sync-calendar
   ```

2. **Test daily workflow:**
   ```bash
   curl -X POST http://localhost:8000/api/workflow/daily
   ```

## Calendar Event Format

The system can parse episodes from calendar events in various formats:

### Supported Title Formats:
- `רוני וברק - פרק 33`
- `Recording: רוני וברק #33`
- `רוני וברק פרק 33`
- `רוני וברק - 33`

### Event Data Extraction:
- **Podcast Name**: Extracted from event title
- **Episode Number**: Extracted from title (supports: "פרק X", "#X", "episode X")
- **Recording Date**: From event start time
- **Studio**: From event location
- **Guest Names**: From description (looks for "אורח", "guest", "with")
- **Notes**: From event description

### Extended Properties (Optional):
You can also store metadata in event extended properties:
- `podcast_id`: Direct podcast ID
- `episode_number`: Episode number
- `studio`: Studio name
- `guest_names`: Guest names

## Troubleshooting

### "Google Calendar API not available"
- Install dependencies: `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`

### "Credentials file not found"
- Check `GOOGLE_CREDENTIALS_PATH` in `.env`
- Ensure file exists at specified path
- Check file permissions

### "Calendar not shared"
- Verify service account email has access to calendar
- Check calendar sharing settings
- Try using calendar ID instead of "primary"

### "No episodes found"
- Check calendar has events for today
- Verify event titles contain podcast names
- Check timezone settings match calendar timezone

### "Permission denied"
- Ensure service account has "See all event details" permission
- Verify Google Calendar API is enabled
- Check service account has correct scopes

## Production Deployment

### Adding the credentials JSON key on Render (or similar)

You have **two options**; use one of them.

#### Option A: Secret File (recommended on Render)

1. In **Render Dashboard** → your **backend** Web Service → **Environment**.
2. Scroll to **Secret Files**.
3. Click **Add Secret File**.
4. **Filename:** `google-service-account.json` (or any name you like).
5. **Contents:** Paste the **entire** contents of your downloaded Google service account JSON key file.
6. Save. Render mounts secret files at `/etc/secrets/` at runtime.
7. Add an **environment variable**:
   - Key: `GOOGLE_CREDENTIALS_PATH`
   - Value: `/etc/secrets/google-service-account.json` (match the filename you used).
8. Set `GOOGLE_CALENDAR_ENABLED=true` and any other Google Calendar env vars. Redeploy the backend.

#### Option B: Environment variable (JSON string)

1. Open your downloaded service account JSON file and copy its **entire** contents (one line or pretty-printed).
2. In **Render Dashboard** → backend → **Environment** → **Add Environment Variable**.
3. Key: `GOOGLE_CREDENTIALS_JSON`
4. Value: Paste the full JSON (as a single line; Render accepts multiline, but avoid extra quotes/escaping).
5. Set `GOOGLE_CALENDAR_ENABLED=true`. Do **not** set `GOOGLE_CREDENTIALS_PATH` when using this option.
6. Save and redeploy.

The app uses `GOOGLE_CREDENTIALS_JSON` if set; otherwise it uses `GOOGLE_CREDENTIALS_PATH` to load from a file.

**Important:** Never commit the JSON key to git. Locally, keep it in `backend/credentials/` and ensure `credentials/` is in `.gitignore`.

### Set up scheduled sync (required for automatic import)

   The app does **not** poll Google Calendar by itself. You must call the workflow endpoints on a schedule:

   - **Daily:** Call `POST /api/workflow/daily` each morning (e.g. 8 AM). This processes today’s episodes and creates studio preparation tasks.
   - **Optional:** Call `POST /api/workflow/sync-calendar?days_ahead=7` periodically to import/update upcoming events into the database.

   **On Render:** Add a [Cron Job or external cron](RENDER_DEPLOYMENT.md#google-calendar-run-daily-import-cron) that POSTs to your backend URL. See RENDER_DEPLOYMENT.md for step-by-step options.

3. **Monitor logs:**
   - Check for authentication errors
   - Monitor API quota usage
   - Set up alerts for sync failures

## API Endpoints

### POST `/api/workflow/daily`
Triggers daily workflow:
- Fetches today's episodes from calendar
- Creates studio preparation tasks

### POST `/api/workflow/sync-calendar?days_ahead=7`
Syncs calendar events to database:
- Fetches upcoming events (default: 7 days)
- Creates/updates episodes
- Returns count of synced episodes
