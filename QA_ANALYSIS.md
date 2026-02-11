# QA Analysis: Google Calendar Integration & Workflow Automation

## Feature Summary

- **Daily workflow** (`POST /api/workflow/daily`): Fetches today’s episodes from Google Calendar (or DB fallback), deletes stale studio-prep tasks, creates studio preparation tasks for each episode.
- **Calendar sync** (`POST /api/workflow/sync-calendar?days_ahead=N`): Syncs upcoming calendar events to episodes (create/update); only processes events whose title matches a known podcast name or alias (no auto-creation of podcasts in this path for “today” flow; sync path also only matches existing podcasts).
- **Event parsing**: Title parsing (Hebrew/English, single/multiple episode numbers, ranges), extraction of date, location, description, guests, extended properties.
- **Workflow automation**: Studio prep → recording → editing/reels → publishing; task status sync with client approval; stale studio-prep task cleanup.

---

## 1. Edge Cases

### 1.1 Event title parsing (`parse_event_title`)

| Edge case | Risk | Current behavior / note |
|-----------|------|--------------------------|
| Empty or `None` title | Low | Returns all-null result; callers may skip. |
| Title with no episode number | Medium | `episode_numbers` empty; podcast name = stripped title. One “episode” with `episode_number=None` can be created. |
| Multiple patterns in one title (e.g. "פרק 33 ו-34" and "33-34") | Medium | Order of regex and `seen` set can dedupe; range limited to `high - low <= 10`. |
| Very large range (e.g. "1-100") | Low | Capped by `(high - low) <= 10`; only 33–34 style or single numbers used. |
| Episode number with leading zeros ("פרק 033") | Low | Treated as "33"; stored as string. |
| Title only digits | Medium | May be parsed as podcast name + no episode number or single number at end. |
| Unicode / RTL / mixed scripts | Medium | Regex is ASCII + Hebrew; other scripts may not match "פרק"/"episode". |
| Duplicate numbers ("33, 33") | Low | `seen` set keeps one. |
| Negative or zero in range | Low | "0-5" could be parsed; business rule for “episode 0” not defined. |

### 1.2 Date/time handling

| Edge case | Risk | Note |
|-----------|------|------|
| All-day event (`date` only) | Low | Parsed as `date + T00:00:00+00:00`. |
| Event with `start.dateTime` in non-UTC | Medium | `.replace('Z', '+00:00')` assumes ISO format; other offsets may not normalize correctly. |
| Missing `start` or invalid ISO string | High | `datetime.fromisoformat` can raise; not caught in `extract_episode_data_from_event`. |
| Recording date in past for “today” | Low | Episode still created; studio prep due date set to “now” if in past. |

### 1.3 Podcast matching (get_todays_episodes / sync)

| Edge case | Risk | Note |
|-----------|------|------|
| Event title matches multiple podcasts (substring) | Medium | Longest match wins; ties not defined. |
| Alias equals another podcast’s name | Low | Exact alias match first; then name. |
| Empty podcast name after stripping numbers | Medium | `find_or_create_podcast("")` returns None; event skipped in sync. |
| Case sensitivity | Low | Exact then `ilike` for name and alias. |
| Sync path: no podcast/alias in DB for title | Low | Event skipped (no auto-create in current sync/daily logic for “recognized” podcast). |

### 1.4 Episode create/update

| Edge case | Risk | Note |
|-----------|------|------|
| Match on (podcast_id, episode_number, recording_date same day) | Medium | Two events same day, same number: one episode updated twice (last write wins). |
| Episode number `None` | Medium | Matching uses `episode_number` and `recording_date`; if both None, no match → multiple “blank” episodes possible for same event. |
| Update only fills empty fields | Low | `if event_data.get('studio') and not episode.studio` etc.; existing data not overwritten. |

### 1.5 Calendar / API

| Edge case | Risk | Note |
|-----------|------|------|
| Calendar disabled or libs missing | Low | Fallback to DB for “today”; sync returns 0. |
| Invalid credentials / file missing | Low | `get_calendar_service()` returns None; fallback. |
| API rate limit or 5xx | Medium | HttpError/Exception caught; daily falls back to DB; sync returns 0. |
| Calendar ID invalid or not shared | Medium | API error; same fallbacks. |
| `days_ahead` negative or very large | Low | Query default or passed through; very large could be slow. |

### 1.6 Workflow automation

| Edge case | Risk | Note |
|-----------|------|------|
| Episode has no `recording_date` | Low | Due dates for tasks stay None. |
| Due date in past | Low | Studio prep/recording due set to “now” (naive vs aware comparison). |
| Episode has no `podcast` (orphan) | High | `create_studio_preparation_task` uses `episode.podcast` for default_studio_settings; could raise. |
| Rejection after “approved” | Low | Editing/reels task reset to IN_PROGRESS. |
| Publishing task: only one of editing/reels approved | Low | Publishing not created until both approved. |
| Stale studio-prep deletion: timezone of `due_date` | Medium | Cutoff uses UTC; if DB stores naive local, comparison may be wrong. |

---

## 2. Test Scenarios (manual / exploratory)

- **Happy path**: Calendar enabled, valid credentials, one event per podcast with clear title → episodes and studio-prep tasks created.
- **Fallback**: Disable calendar or break credentials → daily uses DB; sync returns 0.
- **Multiple episodes in one event**: Title "Podcast - פרק 33 ו-34" → two episodes, two studio-prep tasks.
- **Update existing**: Run sync twice with same event → episode updated, no duplicate.
- **No match**: Event title unknown to aliases/podcasts → skipped (no new podcast in daily/sync).
- **Empty title**: Event with no summary → skipped.
- **Invalid date in event**: Malformed `start.dateTime` → one event fails; others still processed (if error caught).
- **Task idempotency**: Call daily twice → no duplicate studio-prep tasks.
- **Stale cleanup**: Create studio-prep task with due date >1 day ago → run daily → task deleted.
- **Client approval**: Set editing approved → editing task DONE; set reels approved → reels DONE; set both → publishing task created.

---

## 3. Assumptions to Validate

1. **Event title format**: Production calendar events follow one of the documented patterns (e.g. "רוני וברק - פרק 33", "Recording: Name #33"). Unusual formats may yield wrong or null podcast/episode number.
2. **Timezone**: “Today” is computed in UTC; calendar events are requested in UTC. If events are created in a different timezone, “today” boundaries may not match user expectation (e.g. Asia/Jerusalem midnight vs UTC).
3. **One event = one or more episodes**: Back-to-back same event for episodes 33 and 34 is supported; more than ~10 in a range is capped by the parser.
4. **No new podcasts from calendar**: Only events whose title matches an existing podcast or alias create/update episodes; no automatic podcast creation in daily/sync flow (find_podcast_from_event_title returns None → skip).
5. **Stale threshold**: Studio preparation tasks older than 1 day (UTC) are deleted; product expectation may be “same day” or different TZ.
6. **DB datetime storage**: Episodes/tasks store datetimes; if DB uses naive UTC, comparison with `datetime.now(timezone.utc)` after stripping tzinfo is assumed consistent.
7. **Extended properties**: Optional; if used, keys are `podcast_id`, `episode_number`, `studio`, `guest_names` (private).
8. **Guest/description parsing**: Hebrew “אורח” and English “guest”/“with” patterns; other languages not assumed.

---

## 4. Automated Tests (see `backend/tests/`)

- **Unit**: `parse_event_title`, `extract_episode_data_from_event` (no DB).
- **DB**: Podcast lookup by name/alias, substring match, find_or_create_podcast; create_or_update_episode (match vs new).
- **Workflow**: Create studio-prep task (idempotent, due date in past); process_daily_workflow with mocked “today” episodes.
- **API**: `POST /api/workflow/daily` and `POST /api/workflow/sync-calendar` return 200 and JSON shape; behavior under exception (500).

Run from backend: `python -m pytest tests/ -v` (or `pytest tests/ -v`). Requires `pytest`, `pytest-asyncio`, `pytest-cov`; see `backend/requirements.txt` and `backend/pytest.ini`.
