# Quick Deployment Reference

## Fastest Path to Production

### 1. Backend (5 minutes)

**Using Render (recommended):**

1. Push code to GitHub
2. Follow [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) to create backend and frontend
3. Set environment variables in the Render dashboard
4. Deploy

**Using VPS:**

```bash
# On server
git clone <repo>
cd podcast-task-manager/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with production values
python migrate_db.py
python migrate_workflow_fields.py
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend (3 minutes)

```bash
cd frontend
npm install
npm run build
# Deploy to Render (see RENDER_DEPLOYMENT.md) or upload dist/ to any static host
```

### 3. Environment Variables

**Backend `.env`:**

```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
GOOGLE_CALENDAR_ENABLED=true
GOOGLE_CREDENTIALS_PATH=./credentials/google-service-account.json
CORS_ORIGINS=https://yourdomain.com
```

**Frontend `.env.production`:**

```bash
VITE_API_BASE_URL=https://api.yourdomain.com/api
```

### 4. Google Calendar Setup

1. Create service account in Google Cloud
2. Download JSON credentials
3. Share calendar with service account email
4. Upload credentials to server

### 5. Scheduled Tasks

```bash
# Add to crontab (crontab -e)
0 8 * * * curl -X POST https://api.yourdomain.com/api/workflow/daily
```

## Recommended Hosting

- **Render** (recommended): Backend (Web Service) + Frontend (Static Site) — see **[RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)**.
- **Database**: Render PostgreSQL or another managed PostgreSQL.

## Security Checklist

- [ ] HTTPS enabled
- [ ] Strong database password
- [ ] Credentials stored securely
- [ ] CORS configured correctly
- [ ] Firewall configured
- [ ] Regular backups set up

See `DEPLOYMENT.md` for detailed instructions.
