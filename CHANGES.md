# Changes Made to Match New Product Spec

## Major Architectural Changes

### 1. Engineer Assignments Moved to Episode Level
- **Before**: Engineers were assigned via separate Task entities
- **After**: Engineers are assigned directly to episodes via three fields:
  - `recording_engineer_id` - Engineer responsible for recording (הקלטה)
  - `editing_engineer_id` - Engineer responsible for editing (עריכה)
  - `reels_engineer_id` - Engineer responsible for reels
- **Rationale**: Matches the actual workflow where engineers are assigned at episode level, not task level

### 2. Card Name Moved to Episode
- **Before**: `card_name` was on Task entity
- **After**: `card_name` is now on Episode entity
- **Rationale**: Cards organize episodes, not individual tasks

### 3. Reels Notes Added
- Added `reels_notes` field to Episode model
- Separate from general `episode_notes`
- Matches CSV structure where reels have their own notes column

### 4. Task Model Updated
- Changed `owner_id` to `assigned_to` for clarity
- Removed `card_name` from Task (now on Episode)
- Tasks are now optional/additional tracking beyond episode-level assignments

## New Features

### Engineer/Team View
- New "Engineers" tab in navigation
- Shows all team members with assignment counts
- Click on an engineer to see:
  - All episodes assigned to them (by role: recording, editing, reels)
  - Upcoming recording sessions
  - Additional tasks assigned
  - Filter by role (recording, editing, reels, or all)

### Enhanced Episode Management
- Episode form now includes:
  - Card name field
  - Recording engineer dropdown
  - Editing engineer dropdown
  - Reels engineer dropdown
  - Reels notes field
- Episodes table shows assigned engineers in a dedicated column

### Updated CSV Import
- Maps CSV columns to episode-level engineer assignments:
  - Column 10 (הקלטה) → `recording_engineer_id`
  - Column 11 (עריכה) → `editing_engineer_id`
  - Column 12 (reels) → `reels_engineer_id`
  - Column 13 (הערות לרילס) → `reels_notes`
  - Column 9 (על איזה כרטיס) → `card_name`

## Database Migration

If you have an existing database, run:
```bash
python migrate_db.py
```

This will:
- Add new columns to episodes table
- Migrate data from tasks to episode-level assignments (if needed)
- Create indexes for performance

## UI Improvements

- **Clearer Navigation**: Added Engineers tab with icon
- **Better Episode Display**: Shows engineers directly in episodes table
- **Intuitive Engineer View**: Easy-to-understand layout showing assignments by role
- **Improved Forms**: Episode modal now clearly shows all engineer assignment options
- **Visual Indicators**: Color-coded role badges (recording=purple, editing=blue, reels=pink)

## API Changes

### New Endpoints
- `GET /api/engineers` - Get all engineers summary
- `GET /api/engineers/{id}/episodes` - Get engineer's episodes
- `GET /api/engineers/{id}/upcoming` - Get engineer's upcoming recordings
- `GET /api/engineers/{id}/tasks` - Get engineer's tasks and assignments

### Updated Endpoints
- Episode endpoints now return engineer relationships
- Task endpoints use `assigned_to` instead of `owner_id`
- All endpoints use eager loading to prevent N+1 queries

## Breaking Changes

⚠️ **Note**: If you have existing data:
1. Run `migrate_db.py` to add new columns
2. Re-import your CSV to populate engineer assignments correctly
3. Tasks with `owner_id` will need to be updated to use `assigned_to`
