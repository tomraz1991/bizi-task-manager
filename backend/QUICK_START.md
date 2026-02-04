# Quick Start Guide

## Backend Setup

1. **Make sure you're in the backend directory:**
```bash
cd /Users/tom.raz/dev/podcast-task-manager/backend
```

2. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies (THIS IS THE STEP YOU'RE MISSING):**
```bash
pip install -r requirements.txt
```

This will install:
- fastapi
- uvicorn
- sqlalchemy
- pydantic
- python-dateutil
- And other dependencies

4. **Initialize the database:**
```bash
python init_db.py
```

5. **Start the server:**
```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Frontend Setup (in a new terminal)

1. **Navigate to frontend:**
```bash
cd /Users/tom.raz/dev/podcast-task-manager/frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start the dev server:**
```bash
npm run dev
```

## Troubleshooting

**If you get "ModuleNotFoundError":**
- Make sure the virtual environment is activated (you should see `(venv)` in your prompt)
- Run `pip install -r requirements.txt` again
- Check that you're using the correct Python: `which python` should point to `venv/bin/python`

**If pip install fails:**
- Check your internet connection
- Try: `pip install --upgrade pip` first
- Then: `pip install -r requirements.txt`
