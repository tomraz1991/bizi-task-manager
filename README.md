# Podcast Task Manager

A production-ready task management application for recording studios, designed to track podcast production workflows from recording through publishing.

## Features

- **Episode Management**: Track episodes with metadata (recording dates, studios, guests, status)
  - Assign engineers directly to episodes (recording, editing, reels engineers)
  - Track card names for organization
  - Store episode and reels notes separately
- **Task Management**: Optional/additional task tracking beyond episode-level assignments
- **Engineer View**: Each engineer can see their upcoming recordings and all assignments
- **Notifications**: Browser and in-app notifications for upcoming recording sessions and due tasks
- **Dashboard**: Overview of production status, statistics, and urgent items
- **CSV Import**: Import existing data from CSV files with automatic engineer assignment
- **Modern UI**: Clean, intuitive interface built with React and Tailwind CSS

## Tech Stack

### Backend

- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Database (can be upgraded to PostgreSQL for production)
- **Google Calendar API**: Automatic episode discovery and task creation

### Frontend

- **React**: UI library
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Vite**: Build tool
- **React Router**: Navigation
- **Axios**: HTTP client

## Setup

### Backend Setup

**Important:** The backend server must be running before starting the frontend!

1. Navigate to the backend directory:

```bash
cd backend
```

2. **Option A: Use the setup script (recommended):**

```bash
bash setup.sh
```

3. **Option B: Manual setup:**

   - Create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

   - Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   - Initialize the database:

   ```bash
   python init_db.py
   ```

4. **Start the server:**

   - Make sure your virtual environment is activated:

   ```bash
   source venv/bin/activate
   ```

   - Run the server (use `python3` or the venv's python explicitly):

   ```bash
   python3 main.py
   # OR
   ./venv/bin/python main.py
   # OR use the run script:
   bash run.sh
   ```

   **If you get "ModuleNotFoundError" even after installing:**

   - Check which Python you're using: `which python` should show `.../venv/bin/python`
   - If not, use `python3` instead of `python`
   - Or explicitly use: `./venv/bin/python main.py`

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

**Troubleshooting:**

- If you get `ModuleNotFoundError`, make sure you've activated the virtual environment (`source venv/bin/activate`)
- If pip install fails, check your internet connection
- Make sure you're using Python 3.9 or higher

### Frontend Setup

**Make sure the backend is running first!** (See Backend Setup above)

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

**Alternative:** Use the startup script from the project root:

```bash
./start_frontend.sh
# or
bash start_frontend.sh
```

### Quick Start (Both Servers)

Open two terminal windows:

**Terminal 1 - Backend:**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
python main.py
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:3000` in your browser.

## Usage

### Importing CSV Data

1. Navigate to the API documentation at `http://localhost:8000/docs`
2. Find the `/api/import/csv` endpoint
3. Upload your CSV file (format should match the Hebrew CSV structure)

### Notifications

The app will request browser notification permissions on first load. Notifications will appear for:

- Upcoming recording sessions (within 7 days)
- Due tasks (within 7 days)
- Overdue tasks

### Managing Episodes and Tasks

- **Dashboard**: View overview statistics and urgent notifications
- **Episodes**: Browse and filter episodes by podcast, status, and search terms. Assign engineers directly to episodes.
- **Tasks**: View and manage additional tasks (optional tracking beyond episode assignments)
- **Engineers**: View each engineer's assignments, upcoming recordings, and workload

## Project Structure

```
podcast-task-manager/
├── backend/
│   ├── api/           # API endpoints
│   ├── models.py      # Database models
│   ├── schemas.py     # Pydantic schemas
│   ├── database.py    # Database configuration
│   └── main.py        # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts
│   │   ├── pages/         # Page components
│   │   └── api.ts         # API client
│   └── package.json
└── docs/
    └── task-manager-spec.md
```

## API Endpoints

### Podcasts

- `GET /api/podcasts` - List all podcasts
- `GET /api/podcasts/{id}` - Get podcast details
- `POST /api/podcasts` - Create podcast
- `PUT /api/podcasts/{id}` - Update podcast
- `DELETE /api/podcasts/{id}` - Delete podcast

### Episodes

- `GET /api/episodes` - List episodes (with filters)
- `GET /api/episodes/{id}` - Get episode details
- `GET /api/episodes/upcoming/recordings` - Get upcoming recordings
- `POST /api/episodes` - Create episode
- `PUT /api/episodes/{id}` - Update episode
- `DELETE /api/episodes/{id}` - Delete episode

### Tasks

- `GET /api/tasks` - List tasks (with filters)
- `GET /api/tasks/{id}` - Get task details
- `GET /api/tasks/due/upcoming` - Get due tasks
- `GET /api/tasks/overdue` - Get overdue tasks
- `POST /api/tasks` - Create task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

### Users

- `GET /api/users` - List users
- `GET /api/users/{id}` - Get user details
- `POST /api/users` - Create user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

### Engineers

- `GET /api/engineers` - Get summary of all engineers with assignment counts
- `GET /api/engineers/{engineer_id}/episodes` - Get episodes assigned to an engineer (filter by role)
- `GET /api/engineers/{engineer_id}/upcoming` - Get upcoming recordings for an engineer
- `GET /api/engineers/{engineer_id}/tasks` - Get all tasks and episode assignments for an engineer

### Notifications

- `GET /api/notifications` - Get all notifications

### Import

- `POST /api/import/csv` - Import data from CSV (maps engineers to episode-level assignments)

## Development

### Running Tests

TODO: Add test suite

### Code Style

- Backend: Follow PEP 8
- Frontend: ESLint + Prettier (TODO: Add configuration)

## Deployment

For production deployment, see [DEPLOYMENT.md](./DEPLOYMENT.md) for comprehensive instructions.

**Deploy both backend and frontend on Render:** see [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md).

Quick start: See [DEPLOYMENT_QUICK_START.md](./DEPLOYMENT_QUICK_START.md)

## License

MIT
