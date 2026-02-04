# Implementation Checklist

## Critical Bugs & Edge Cases

### Backend

- [ ] **Fix null handling in episodes.py:32** - Add null handling to `order_by(Episode.recording_date.desc())` using `nullslast()` or filter out nulls
- [ ] **Fix null handling in tasks.py:38** - Add null handling to `order_by(Task.due_date.asc())` using `nullslast()` or filter out nulls
- [ ] **Fix empty string key in import_csv.py:115** - Replace `row.get("", "")` with correct CSV column name or handle empty key properly
- [ ] **Fix bare except clause in import_csv.py:43** - Change `except:` to `except Exception as e:` and add proper error logging
- [ ] **Fix None check in notifications.py:40** - Add null check before calling `strftime()` on `episode.recording_date`
- [ ] **Replace magic number in notifications.py:55** - Replace `days_until = 999` with a named constant (e.g., `FAR_FUTURE_DAYS = 999`)
- [ ] **Add user deletion validation in users.py:81** - Check if user has assigned tasks before allowing deletion, or handle cascade properly

### Frontend

- [ ] **Fix date comparison in Dashboard.tsx:36** - Add null check for `t.due_date` before date comparison
- [ ] **Make baseURL configurable in api.ts:4** - Use environment variable for API base URL instead of hardcoded '/api'

## Code Quality Improvements

### Backend

- [ ] **Replace deprecated datetime.utcnow()** - Update all instances in `models.py` (lines 46, 66, 81, 101) to use `datetime.now(timezone.utc)`
- [ ] **Extract parse_date function** - Move `parse_date()` from `import_csv.py` to a utility module (e.g., `utils.py`)
- [ ] **Add type hints** - Add return type annotations to `get_or_create_user()` and `get_or_create_podcast()` in `import_csv.py`
- [ ] **Extract duplicate code** - Move `task_type_labels` dictionary from `notifications.py` (lines 58-63, 86-91) to a module-level constant
- [ ] **Standardize error messages** - Create consistent error response format across all endpoints
- [ ] **Extract magic numbers** - Replace hardcoded `7` (days) with a constant in relevant files

### Frontend

- [ ] **Replace window.location.reload() in Dashboard.tsx:127** - Use React state management to refresh data instead of full page reload
- [ ] **Extract date calculation logic** - Move complex date calculation from `Dashboard.tsx:36` to a helper function
- [ ] **Extract magic numbers** - Replace hardcoded `7` (days) with a constant

## Architectural Improvements

### Backend

- [ ] **Add transaction management to CSV import** - Implement proper transaction rollback on errors in `import_csv.py`
- [ ] **Add foreign key validation** - Validate `podcast_id` exists before creating episodes, validate `episode_id` exists before creating tasks
- [ ] **Add pagination metadata** - Return total count and pagination info in list endpoints (episodes, tasks, podcasts, users)
- [ ] **Add error handling middleware** - Create global exception handler for consistent error response format
- [ ] **Make CORS configurable** - Move CORS origins from hardcoded values in `main.py:32` to environment variables
- [ ] **Add eager loading** - Use `joinedload()` or `selectinload()` in `notifications.py` to prevent N+1 queries when accessing `task.episode.podcast`

### Frontend

- [ ] **Add loading states** - Show loading indicators during API calls in Dashboard and other pages
- [ ] **Add error boundaries** - Implement React error boundaries to prevent app crashes

## Security Improvements

- [ ] **Add file upload validation** - Validate file size and type in `import_csv.py` before processing CSV file
- [ ] **Restrict CORS configuration** - Replace `allow_methods=["*"]` and `allow_headers=["*"]` with specific allowed methods and headers

## Performance Improvements

- [ ] **Add database indexes** - Create composite indexes for frequently queried combinations (e.g., `(episode_id, status)` for tasks table)

## Documentation

- [ ] **Add missing docstrings** - Add docstrings to functions missing them, including parameters, return values, and exceptions
- [ ] **Add Field descriptions** - Add descriptions to Pydantic `Field()` definitions in `schemas.py` for better API documentation
