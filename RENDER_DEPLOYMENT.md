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
   | `CORS_ORIGINS`  | Leave as `*` for now; after frontend is live, set to your frontend URL, e.g. `https://podcast-task-manager.onrender.com` |

   For Google Calendar (optional):

   | Key                         | Value |
   |-----------------------------|--------|
   | `GOOGLE_CALENDAR_ENABLED`   | `true` |
   | `GOOGLE_CALENDAR_ID`        | your calendar id |
   | `GOOGLE_CREDENTIALS_PATH`   | path to JSON (or use secret file / env JSON) |
   | `GOOGLE_SERVICE_ACCOUNT_EMAIL` | service account email |
   | `GOOGLE_CALENDAR_TIMEZONE`  | e.g. `Asia/Jerusalem` |

5. Click **Create Web Service**. Wait until the first deploy succeeds.
6. Copy the service URL, e.g. `https://podcast-task-manager-api.onrender.com`. You’ll use this for the frontend and for `CORS_ORIGINS`.

### Step 2b: Database

- **Option A – Render PostgreSQL:** In the same Render account, create a **PostgreSQL** instance, then copy the **Internal Database URL** (or External if you prefer) into `DATABASE_URL` for the backend.
- **Option B – SQLite (not recommended for production):** You can omit `DATABASE_URL` to use the default SQLite path. Note: on free tier the filesystem can be ephemeral; use PostgreSQL for real data.

After the first deploy, run migrations once (Render Shell or a one-off job):

```bash
cd backend
pip install -r requirements.txt
python migrate_db.py
python migrate_workflow_fields.py
python init_db.py
```

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
   | `VITE_API_BASE_URL`  | `https://YOUR-BACKEND-URL.onrender.com/api` |

   Replace `YOUR-BACKEND-URL` with the backend URL from Step 2 (e.g. `https://podcast-task-manager-api.onrender.com/api`).

5. Click **Create Static Site**. Wait for the build to finish.

---

## Step 4: Lock CORS to your frontend (recommended)

After the frontend is live:

1. Open the **backend** Web Service → **Environment**.
2. Set `CORS_ORIGINS` to your frontend URL only, e.g. `https://podcast-task-manager.onrender.com` (no trailing slash).
3. Save and redeploy the backend if needed.

---

## Step 5: Verify

- Open the **frontend** URL (e.g. `https://podcast-task-manager.onrender.com`). You should see the app.
- Use the UI to create/edit data; it should hit the backend. Check Network tab: requests go to `https://podcast-task-manager-api.onrender.com/api/...`.

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
| Frontend 404 on refresh / direct URL | Render Static Site serves `index.html` for routes; if you see 404, check Publish Directory is `dist` and build succeeded. |
| API requests fail (CORS / network) | Set `VITE_API_BASE_URL` to `https://<backend>.onrender.com/api` and `CORS_ORIGINS` on backend to `https://<frontend>.onrender.com`. |
| **npm E401 / "Sonatype Nexus Repository Manager"** | Your `package-lock.json` had `resolved` URLs pointing at a private registry. The repo lockfile is now using the public registry. If you still see this, set **Build Command** to `npm install --registry https://registry.npmjs.org/ && npm run build`. |
| Database empty after deploy | Run `migrate_db.py`, `migrate_workflow_fields.py`, and `init_db.py` once (Render Shell or one-off job). |

---

## Summary

1. Deploy **backend** as Web Service (root `backend`, Python 3.11, `uvicorn` start command).
2. Add `DATABASE_URL` (and optional Google Calendar vars); run migrations once.
3. Deploy **frontend** as Static Site (root `frontend`, publish `dist`).
4. Set **frontend** env `VITE_API_BASE_URL` to `https://<backend>.onrender.com/api`.
5. Set **backend** `CORS_ORIGINS` to your frontend URL.

After that, both backend and frontend run on Render and work together.
