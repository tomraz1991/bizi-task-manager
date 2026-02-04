# Production Deployment Guide

This guide covers deploying the Podcast Task Manager to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Deployment](#backend-deployment)
3. [Frontend Deployment](#frontend-deployment)
4. [Database Setup](#database-setup)
5. [Environment Configuration](#environment-configuration)
6. [Google Calendar Setup](#google-calendar-setup)
7. [Security Considerations](#security-considerations)
8. [Hosting Options](#hosting-options)
9. [Monitoring & Maintenance](#monitoring--maintenance)

## Prerequisites

- Production server (VPS, cloud instance, etc.)
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt recommended)
- Google Cloud account (for Calendar integration)
- Basic knowledge of Linux/server administration

## Backend Deployment

### Option 1: Traditional VPS/Server

#### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+
sudo apt install python3.9 python3.9-venv python3-pip -y

# Install Nginx (for reverse proxy)
sudo apt install nginx -y

# Install PostgreSQL (recommended for production) or use SQLite
sudo apt install postgresql postgresql-contrib -y
```

#### 2. Application Setup

```bash
# Create application user
sudo adduser --disabled-password --gecos "" podcastapp
sudo su - podcastapp

# Clone repository or upload files
cd /home/podcastapp
git clone <your-repo-url> podcast-task-manager
cd podcast-task-manager/backend

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
nano .env  # Edit with production values
```

#### 3. Database Migration

```bash
# Run migrations
./venv/bin/python migrate_db.py
./venv/bin/python migrate_workflow_fields.py

# Initialize database
./venv/bin/python init_db.py
```

#### 4. Create Systemd Service

Create `/etc/systemd/system/podcast-api.service`:

```ini
[Unit]
Description=Podcast Task Manager API
After=network.target

[Service]
Type=simple
User=podcastapp
WorkingDirectory=/home/podcastapp/podcast-task-manager/backend
Environment="PATH=/home/podcastapp/podcast-task-manager/backend/venv/bin"
ExecStart=/home/podcastapp/podcast-task-manager/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable podcast-api
sudo systemctl start podcast-api
sudo systemctl status podcast-api
```

#### 5. Nginx Configuration

Create `/etc/nginx/sites-available/podcast-api`:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/podcast-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 6. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal is set up automatically
```

### Option 2: Docker Deployment

#### 1. Create Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/podcast_db
      - GOOGLE_CALENDAR_ENABLED=true
      - GOOGLE_CREDENTIALS_PATH=/app/credentials/google-service-account.json
    volumes:
      - ./backend/credentials:/app/credentials:ro
      - ./backend/data:/app/data
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=podcast_user
      - POSTGRES_PASSWORD=your_secure_password
      - POSTGRES_DB=podcast_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

#### 3. Deploy

```bash
docker-compose up -d
```

### Option 3: Cloud Platforms

#### Railway
1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically

#### Render
1. Create new Web Service
2. Connect repository
3. Set build command: `cd backend && pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### Heroku
```bash
# Create Procfile in backend/
web: uvicorn main:app --host 0.0.0.0 --port $PORT

# Deploy
heroku create podcast-task-manager-api
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

## Frontend Deployment

### Option 1: Static Hosting (Recommended)

#### Build for Production

```bash
cd frontend
npm install
npm run build
```

This creates a `dist/` folder with optimized production files.

#### Deploy to Various Platforms

**Vercel:**
```bash
npm install -g vercel
vercel --prod
```

**Netlify:**
```bash
npm install -g netlify-cli
netlify deploy --prod
```

**Cloudflare Pages:**
- Connect GitHub repository
- Build command: `npm run build`
- Build output: `dist`

**Nginx Static Hosting:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /var/www/podcast-task-manager/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Option 2: Same Server as Backend

```bash
# Build frontend
cd frontend
npm run build

# Copy to web server
sudo cp -r dist/* /var/www/podcast-task-manager/
```

## Database Setup

### PostgreSQL (Recommended for Production)

```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE podcast_db;
CREATE USER podcast_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE podcast_db TO podcast_user;
\q
```

Update `.env`:
```bash
DATABASE_URL=postgresql://podcast_user:secure_password@localhost:5432/podcast_db
```

### SQLite (Simple but Limited)

For small deployments, SQLite works but has limitations:
- No concurrent writes
- File-based (backup considerations)
- Not recommended for high traffic

## Environment Configuration

### Backend `.env` (Production)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/podcast_db

# Google Calendar
GOOGLE_CALENDAR_ENABLED=true
GOOGLE_CALENDAR_ID=primary
GOOGLE_CREDENTIALS_PATH=/path/to/google-service-account.json
GOOGLE_SERVICE_ACCOUNT_EMAIL=your-service-account@project.iam.gserviceaccount.com
GOOGLE_CALENDAR_TIMEZONE=Asia/Jerusalem
GOOGLE_CALENDAR_LOOKAHEAD_DAYS=7

# CORS (Update with your frontend domain)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Security (Add these)
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=api.yourdomain.com
```

### Frontend Environment

Create `frontend/.env.production`:

```bash
VITE_API_BASE_URL=https://api.yourdomain.com/api
```

## Google Calendar Setup

1. **Create Production Service Account:**
   - Go to Google Cloud Console
   - Create new project or use existing
   - Enable Google Calendar API
   - Create service account
   - Download JSON credentials

2. **Share Calendar:**
   - Share production calendar with service account email
   - Grant "See all event details" permission

3. **Store Credentials Securely:**
   ```bash
   # On server
   mkdir -p /home/podcastapp/podcast-task-manager/backend/credentials
   # Upload credentials file
   chmod 600 /home/podcastapp/podcast-task-manager/backend/credentials/google-service-account.json
   ```

4. **Set Up Scheduled Tasks:**
   ```bash
   # Add to crontab
   crontab -e
   
   # Run daily workflow every morning at 8 AM
   0 8 * * * curl -X POST https://api.yourdomain.com/api/workflow/daily
   
   # Sync calendar every 6 hours
   0 */6 * * * curl -X POST https://api.yourdomain.com/api/workflow/sync-calendar
   ```

## Security Considerations

### 1. Environment Variables
- Never commit `.env` files
- Use secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)
- Rotate credentials regularly

### 2. Database Security
- Use strong passwords
- Restrict database access to application server only
- Enable SSL for database connections
- Regular backups

### 3. API Security
- Enable HTTPS only
- Add rate limiting
- Consider API authentication (JWT tokens)
- Validate all inputs

### 4. File Permissions
```bash
# Secure credentials
chmod 600 credentials/google-service-account.json
chown podcastapp:podcastapp credentials/google-service-account.json

# Application files
chmod 755 /home/podcastapp/podcast-task-manager
```

### 5. Firewall
```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

## Hosting Options

### Budget-Friendly
- **DigitalOcean Droplet**: $6-12/month
- **Linode**: $5-10/month
- **Vultr**: $6-12/month

### Managed Services
- **Railway**: Pay-as-you-go
- **Render**: Free tier available
- **Fly.io**: Generous free tier

### Enterprise
- **AWS**: EC2 + RDS + CloudFront
- **Google Cloud**: Compute Engine + Cloud SQL
- **Azure**: App Service + Database

## Monitoring & Maintenance

### 1. Logging

Add logging configuration in `backend/main.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/podcast-api.log'),
        logging.StreamHandler()
    ]
)
```

### 2. Health Checks

The API already has a health endpoint:
```bash
curl https://api.yourdomain.com/api/health
```

### 3. Backups

**Database Backups:**
```bash
# PostgreSQL
pg_dump -U podcast_user podcast_db > backup_$(date +%Y%m%d).sql

# SQLite
cp podcast_task_manager.db backup_$(date +%Y%m%d).db
```

**Automated Backups:**
```bash
# Add to crontab
0 2 * * * pg_dump -U podcast_user podcast_db > /backups/db_$(date +\%Y\%m\%d).sql
```

### 4. Updates

```bash
# Pull latest code
cd /home/podcastapp/podcast-task-manager
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Run migrations if needed
./venv/bin/python migrate_db.py

# Restart service
sudo systemctl restart podcast-api
```

### 5. Monitoring Tools

- **Uptime Monitoring**: UptimeRobot, Pingdom
- **Error Tracking**: Sentry
- **Analytics**: Google Analytics, Plausible
- **Server Monitoring**: New Relic, Datadog

## Deployment Checklist

- [ ] Server provisioned and secured
- [ ] Domain name configured
- [ ] SSL certificate installed
- [ ] Database set up and migrated
- [ ] Environment variables configured
- [ ] Google Calendar credentials uploaded
- [ ] Backend deployed and running
- [ ] Frontend built and deployed
- [ ] CORS configured correctly
- [ ] Scheduled tasks configured
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] Documentation updated
- [ ] Team access configured

## Quick Start Commands

```bash
# Backend
cd backend
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env
python migrate_db.py
python migrate_workflow_fields.py
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run build
# Deploy dist/ folder
```

## Troubleshooting

### Backend won't start
- Check logs: `sudo journalctl -u podcast-api -f`
- Verify environment variables
- Check database connection
- Verify port availability

### Frontend can't connect to API
- Check CORS settings
- Verify API URL in frontend `.env`
- Check network/firewall rules
- Verify SSL certificates

### Google Calendar not working
- Verify credentials file path
- Check calendar sharing
- Verify API is enabled
- Check service account permissions

## Support

For issues or questions:
1. Check logs first
2. Review error messages
3. Verify configuration
4. Check documentation
