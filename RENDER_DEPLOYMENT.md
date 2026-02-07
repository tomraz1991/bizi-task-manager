# Deploy Backend and Frontend on Render

This guide walks you through deploying **both** the FastAPI backend and the React/Vite frontend on [Render](https://render.com), so everything runs in one place.

## Overview

| Service   | Type         | Root directory | Build / Start |
|----------|--------------|----------------|----------------|
| Backend  | Web Service  | `backend`      | Build: `pip install -r requirements.txt` → Start: `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Frontend | Static Site  | `frontend`     | Build: `npm install && npm run build` → Publish: `dist` |

You’ll deploy the **backend first**, then the **frontend** (so the frontend can point to the backend URL).

---

## Step 1: Prepare the repo

- Push your code to GitHub (or GitLab/Bitbucket).
- Ensure you have:
  - **Backend:** `backend/requirements.txt`, `backend/main.py`, `.python-version` with `3.11` (or `backend/.python-version`).
  - **Frontend:** `frontend/package.json`, `frontend/vite.config.ts`.

---

## Step 2: Create the Backend (Web Service)

1. In [Render Dashboard](https://dashboard.render.com), click **New** → **Web Service**.
2. Connect your repository and select the repo.
3. Configure:
   - **Name:** e.g. `podcast-task-manager-api`
   - **Region:** choose one
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Environment variables** (add in the Environment tab):

   | Key             | Value / notes |
   |-----------------|----------------|
   | `PYTHON_VERSION` | `3.11.11` (avoids 3.13 build issues) |
   | `DATABASE_URL`  | See [Step 2b](#step-2b-database) |
   | `CORS_ORIGINS`  | **Required for frontend.** Set to your frontend URL exactly, e.g. `https://podcast-task-manager.onrender.com` (no trailing slash). You can add this after the frontend is created; until then use `*` to allow all origins (then lock to your frontend URL in Step 4). |

   For Google Calendar (optional): see **[GOOGLE_CALENDAR_SETUP.md](GOOGLE_CALENDAR_SETUP.md)** for how to add the credentials JSON in production. Use either a **Secret File** (path `/etc/secrets/google-service-account.json`) and set `GOOGLE_CREDENTIALS_PATH` to that path, or set **`GOOGLE_CREDENTIALS_JSON`** to the full JSON string.

   | Key                         | Value |
   |-----------------------------|--------|
   | `GOOGLE_CALENDAR_ENABLED`   | `true` |
   | `GOOGLE_CALENDAR_ID`        | your calendar id |
   | `GOOGLE_CREDENTIALS_PATH`   | `/etc/secrets/google-service-account.json` (if using Secret File) |
   | or `GOOGLE_CREDENTIALS_JSON` | full JSON key as string (alternative) |
   | `GOOGLE_SERVICE_ACCOUNT_EMAIL` | service account email |
   | `GOOGLE_CALENDAR_TIMEZONE`  | e.g. `Asia/Jerusalem` |

5. Click **Create Web Service**. Wait until the first deploy succeeds.
6. Copy the service URL, e.g. `https://podcast-task-manager-api.onrender.com`. You’ll use this for the frontend and for `CORS_ORIGINS`.

### Step 2b: Database

- **Option A – Render PostgreSQL:** In the same Render account, create a **PostgreSQL** instance, then copy the **Internal Database URL** (or External if you prefer) into `DATABASE_URL` for the backend.
- **Option B – SQLite (not recommended for production):** You can omit `DATABASE_URL` to use the default SQLite path. Note: on free tier the filesystem can be ephemeral; use PostgreSQL for real data.

**Migrations:** You do **not** need to run migrations or use Render Shell. On each deploy the app runs `init_db()` at startup, which creates all tables from the current models. A new PostgreSQL database will have the correct schema as soon as the backend starts.

---

## Step 3: Create the Frontend (Static Site)

1. In Render Dashboard, click **New** → **Static Site**.
2. Connect the **same** repository.
3. Configure:
   - **Name:** e.g. `podcast-task-manager`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install --registry https://registry.npmjs.org/ && npm run build`
   - **Publish Directory:** `dist`

   (Using `--registry https://registry.npmjs.org/` avoids E401 if your lockfile or environment pointed at a private npm/Nexus registry.)
4. **Environment variable** (required so the app talks to your backend):

   | Key                  | Value |
   |----------------------|--------|
   | `VITE_API_BASE_URL`  | Your backend URL; must end with `/api` (e.g. `https://podcast-task-manager-api.onrender.com/api`). If you set only the origin, the app will append `/api` for you. |

   Replace with your actual backend URL from Step 2.

5. Click **Create Static Site**. Wait for the build to finish.

---

## Step 4: Fix CORS (required for frontend to work)

If the frontend gets a CORS error when calling the API:

1. Open the **backend** Web Service on Render → **Environment**.
2. Set `CORS_ORIGINS` to your **frontend** URL exactly, e.g. `https://podcast-task-manager.onrender.com` (no trailing slash, same URL you see in the browser for the app).
3. Save and redeploy the backend.

If you had set `CORS_ORIGINS` to `*`, the backend allows all origins but without credentials. For a specific frontend URL, set it explicitly so credentials work if needed.

---

## Step 5: Verify

- Open the **frontend** URL (e.g. `https://podcast-task-manager.onrender.com`). You should see the app.
- Use the UI to create/edit data; it should hit the backend. Check Network tab: requests go to `https://podcast-task-manager-api.onrender.com/api/...`.

---

## Google Calendar: run daily import (cron)

If you use Google Calendar integration, the app does **not** fetch the calendar by itself. You need to **call the workflow endpoints on a schedule** so that:

1. **Daily workflow** – today’s episodes are processed and studio preparation tasks are created.
2. **Calendar sync** (optional) – upcoming events are imported/updated in the database.

**Yes, you should add a scheduled job** (cron) that hits your backend. Two ways to do it:

### Option A: Render Cron Job

1. In **Render Dashboard** → **New** → **Cron Job**.
2. Connect the **same** repo.
3. **Root Directory:** set to **`backend`**. (Required so the build finds `requirements.txt`; otherwise you get "Could not open requirements file".)
4. **Build Command:** `pip install -r requirements.txt` (or leave default – it runs from `backend/` when Root Directory is set).
5. **Schedule:** e.g. `0 8 * * *` (daily at 08:00 **UTC**). Adjust for your timezone (e.g. Israel: 08:00 local ≈ 05:00 UTC in winter, 06:00 UTC in summer).
6. **Command** (the command that runs on each cron run):
   ```bash
   curl -X POST https://YOUR-BACKEND.onrender.com/api/workflow/daily
   ```
   Replace `YOUR-BACKEND` with your backend service name (e.g. `bizi-task-manager`).
7. (Optional) Add a second cron or a line in the same script to sync the calendar:
   ```bash
   curl -X POST "https://YOUR-BACKEND.onrender.com/api/workflow/sync-calendar?days_ahead=7"
   ```
8. Save. Render will run the job on the schedule (Cron Jobs are billed by run time).

### Option B: External cron / ping service

Use a free external service that calls a URL on a schedule:

- **[cron-job.org](https://cron-job.org)** or **[EasyCron](https://www.easycron.com)** – create a job that does a **POST** to `https://YOUR-BACKEND.onrender.com/api/workflow/daily` once per day (e.g. 08:00 your time).
- Optionally add a second job for `POST .../api/workflow/sync-calendar?days_ahead=7` (e.g. every 6 hours or daily).

**Summary:** Without a cron (or manual calls), calendar events are never imported. Set up one of the options above so `/api/workflow/daily` (and optionally `/api/workflow/sync-calendar`) run on a schedule.

---

## Fix 404 when refreshing a page (e.g. /episodes)

The app is a Single Page Application (SPA): routes like `/episodes` are handled by React Router in the browser. When you **refresh** or open `https://your-frontend.onrender.com/episodes` directly, the server receives a request for `/episodes` and has no file at that path, so it returns 404.

**Fix:** Tell Render to serve `index.html` for all paths so the SPA can load and React Router can handle the route.

1. In **Render Dashboard** → your **frontend** Static Site.
2. Open **Redirects / Rewrites** (in the left sidebar or under Settings).
3. Add a **Rewrite** rule:
   - **Source:** `/*`
   - **Destination:** `/index.html`
   - **Action:** Rewrite (not Redirect)
4. Save. New deploys will use this; you may not need to redeploy.

After this, refreshing `https://bizi-task-manager-1.onrender.com/episodes` (or any route) will serve the app and the correct page will show.

---

## Clear database (PostgreSQL)

To **delete all data** in your Render PostgreSQL database (tables stay, data is removed):

1. **Get the connection URL**  
   In Render Dashboard → your **PostgreSQL** service → **Connect** → copy **External Database URL** (e.g. `postgresql://user:pass@dpg-xxx-a.oregon-postgres.render.com/dbname`).

2. **Run the clear script from your machine** (same repo, backend folder). Use a virtualenv or install deps first:

   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   DATABASE_URL="postgresql://user:pass@host/dbname" .venv/bin/python clear_db.py
   ```
   Use `.venv/bin/python` (or `python3` after activate) so the script runs with the venv that has the dependencies.

   Paste your actual External Database URL in place of `"postgresql://..."`.  
   If the URL points at Render, the script will ask you to type `yes` before clearing.

3. **Result**  
   All rows in `tasks`, `episodes`, `podcasts`, and `users` are deleted. You can import a CSV again from the app.

---

## Optional: Blueprint (render.yaml)

You can define both services in a single **Blueprint** so Render creates them from the repo.

1. Add a `render.yaml` in the **root** of your repo (see the one in this repo).
2. In Render: **New** → **Blueprint**, connect the repo. Render will create the Web Service and Static Site from the YAML.
3. You still must set **manually** in the dashboard:
   - Backend: `DATABASE_URL` (and any Google Calendar vars).
   - Frontend: `VITE_API_BASE_URL` = `https://<your-backend-service-name>.onrender.com/api` (use the actual backend URL Render assigns).

The Blueprint does not know the backend URL in advance, so `VITE_API_BASE_URL` must be set after the first deploy (or after you see the backend URL).

---

## Troubleshooting

| Issue | What to do |
|-------|------------|
| Backend build fails (Rust / maturin / read-only) | Set `PYTHON_VERSION=3.11.11` and ensure Root Directory is `backend`. |
| **404 when refreshing** a route (e.g. /episodes) | Add a **Rewrite** in Render → Frontend → Redirects/Rewrites: Source `/*`, Destination `/index.html`, type Rewrite. See [Fix 404 when refreshing](#fix-404-when-refreshing-a-page-eg-episodes). |
| **CORS error** / "No 'Access-Control-Allow-Origin' header" | Backend now allows any `https://*.onrender.com` origin. Redeploy the backend so the change is live. If you use a custom domain for the frontend, set `CORS_ORIGINS` on the backend to that URL (e.g. `https://bizi-task-manager-1.onrender.com`). |
| **307 Temporary Redirect** then CORS | On free tier the backend can spin down; the first request may get a 307 from Render (no CORS headers). Wait a few seconds and refresh the page so the backend wakes up; the next request should succeed. |
| API requests fail (network) | Set `VITE_API_BASE_URL` to `https://<backend>.onrender.com/api`. Backend allows `*.onrender.com` origins by default. |
| **npm E401 / "Sonatype Nexus Repository Manager"** | Your `package-lock.json` had `resolved` URLs pointing at a private registry. The repo lockfile is now using the public registry. If you still see this, set **Build Command** to `npm install --registry https://registry.npmjs.org/ && npm run build`. |
| Database empty / tables missing | The app creates tables on startup via `init_db()`. Ensure `DATABASE_URL` is set and the backend has started at least once. |

---

## Summary

1. Deploy **backend** as Web Service (root `backend`, Python 3.11, `uvicorn` start command).
2. Add `DATABASE_URL` (and optional Google Calendar vars); run migrations once.
3. Deploy **frontend** as Static Site (root `frontend`, publish `dist`).
4. Set **frontend** env `VITE_API_BASE_URL` to `https://<backend>.onrender.com/api`.
5. Set **backend** `CORS_ORIGINS` to your frontend URL.

After that, both backend and frontend run on Render and work together.
