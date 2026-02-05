# Podcast Task Manager - Product Specification

## Overview

The Podcast Task Manager is a production workflow management system designed to track and coordinate podcast production tasks from recording through publishing. The system manages multiple podcasts, episodes, and associated tasks (recording, editing, reels creation, publishing) with team member assignments and status tracking.

## Core Entities

### Podcast

A podcast show with multiple episodes.

**Attributes:**

- `id`: Unique identifier
- `name`: Podcast name (e.g., "רוני וברק", "סטימצקי", "אפרת וכטל")
- `host`: Primary host name (optional, e.g., "אבי זייתן")
- `default_studio_settings`: Default studio setup for episodes (optional)
- `tasks_time_allowance_days`: How long engineers have to complete all tasks for an episode of this podcast (optional, e.g. "7", "3 days", "1 week")
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Episode

A single episode of a podcast.

**Attributes:**

- `id`: Unique identifier
- `podcast_id`: Reference to parent podcast
- `episode_number`: Episode number or identifier (e.g., "33", "עונה 3 פרק 1", "רילז - 2")
- `recording_date`: Date when episode was recorded (format: DD.MM.YY or DD/MM/YY)
- `studio`: Studio location where recording took place (e.g., "חשמונאים", "גבעון", "TLV")
- `guest_names`: Names of guests featured in the episode (comma-separated)
- `status`: Overall episode status (see Episode Status below)
- `episode_notes`: Free-form notes about the episode
- `drive_link`: Google Drive link to episode files (optional)
- `backup_deletion_date`: Date when episode was deleted from backup (optional)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

**Episode Status Values:**

- `הוקלט` (Recorded) - Episode has been recorded
- `בעריכה` (In Editing) - Episode is currently being edited
- `הופץ` (Published) - Episode has been published/released
- `נשלח ללקוח` (Sent to Client) - Episode has been sent to client for review
- `לא התחילה` (Not Started) - Recording has not begun

### Task

A work item associated with an episode. Each episode can have multiple tasks of different types.

**Attributes:**

- `id`: Unique identifier
- `episode_id`: Reference to parent episode
- `type`: Task type (see Task Types below)
- `status`: Task status (see Task Status below)
- `owner`: User ID assigned to this task (optional)
- `due_date`: Target completion date (optional)
- `completed_at`: Timestamp when task was marked as done (optional)
- `notes`: Free-form notes about the task
- `card_name`: Card/task board identifier (e.g., "roni ve barak", "stimatsky")
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

**Task Types:**

- `recording` (הקלטה) - Recording the episode
- `editing` (עריכה) - Editing the recorded audio/video
- `reels` (reels) - Creating short-form content/reels
- `publishing` - Publishing the final episode

**Task Status Values:**

- `not_started` - Task has not been started
- `in_progress` - Task is currently being worked on
- `blocked` - Task is blocked and cannot proceed
- `done` - Task has been completed
- `skipped` - Task was skipped (not applicable)

### User

A team member who can be assigned to tasks.

**Attributes:**

- `id`: Unique identifier
- `name`: User's name (e.g., "אורי", "אלי", "בניה", "גאיה", "שחר", "יובל", "ליאור", "עדי", "יותם")
- `email`: User's email address (optional)
- `role`: User's role (optional)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Key Features

### 1. Episode Management

- Create, read, update, and delete episodes
- Track episode metadata (recording date, studio, guests, episode number)
- Manage episode status throughout the production lifecycle
- Store links to episode files (e.g., Google Drive)
- Track backup deletion dates

### 2. Task Management

- Create tasks for each episode (recording, editing, reels, publishing)
- Assign tasks to team members
- Track task status and progress
- Set due dates for tasks
- Add notes and comments to tasks
- Mark tasks as complete with timestamps

### 3. Workflow Tracking

- View all tasks across all episodes
- Filter tasks by status, type, owner, or podcast
- Track which team member is responsible for each task type per episode
- Identify bottlenecks and overdue tasks
- View production pipeline status

### 4. Team Collaboration

- Assign multiple team members to different tasks on the same episode
- Track who is responsible for recording, editing, and reels creation
- View workload distribution across team members
- Identify dependencies between tasks

### 5. Reporting & Analytics

- View production statistics (episodes recorded, edited, published)
- Track team productivity
- Identify common bottlenecks
- Generate reports on episode status distribution
- Track time-to-publish metrics

## Data Model Relationships

```
Podcast (1) ──< (many) Episode (1) ──< (many) Task
                                    └──< (many) User (via owner)
```

- One Podcast has many Episodes
- One Episode has many Tasks
- Tasks are assigned to Users (many-to-one relationship)

## Business Rules

1. **Episode Status Progression**: Episodes typically progress through: Not Started → Recorded → In Editing → Sent to Client → Published

2. **Task Dependencies**:

   - Editing tasks cannot start until recording is complete
   - Publishing tasks cannot start until editing is complete
   - Reels can be created independently or after editing

3. **Multiple Tasks per Episode**: An episode can have multiple tasks of the same type (e.g., multiple reels, multiple editing passes)

4. **Card/Task Board**: Tasks are organized by "card_name" which groups related episodes (often by podcast name in English/transliterated form)

5. **Guest Tracking**: Guest names are stored as free-form text, allowing for multiple guests per episode

6. **Studio Tracking**: Studio information helps coordinate recording logistics and resource allocation

## Data Import

The system should support importing data from CSV files with the following columns:

- Podcast name (Hebrew)
- Recording date
- Studio
- Episode number
- Guest names
- Status
- Episode notes
- Card/Task board name
- Recording person assignment
- Editing person assignment
- Reels person assignment
- Reels notes
- Drive link
- Backup deletion date

## Technical Requirements

### Data Storage

- Persistent storage for podcasts, episodes, tasks, and users
- Support for date/time fields with timezone awareness
- Support for optional/nullable fields
- Unique constraints on entity IDs

### API Requirements

- RESTful API for CRUD operations on all entities
- Filtering and sorting capabilities
- Pagination for large result sets
- Search functionality (by podcast name, guest name, etc.)

### User Interface Requirements

- Dashboard showing current production status
- Episode list view with filtering and sorting
- Task board/Kanban view for task management
- Episode detail view with all associated tasks
- Team member workload view
- Reporting and analytics views

## Future Enhancements (TODOs)

- [ ] Email notifications for task assignments and status changes
- [ ] Calendar integration for recording dates
- [ ] File upload and management for episode assets
- [ ] Integration with Google Drive API for automatic link validation
- [ ] Time tracking for tasks
- [ ] Budget and cost tracking per episode
- [ ] Client portal for episode review and approval
- [ ] Mobile app for on-the-go task updates
- [ ] Automated status updates based on task completion
- [ ] Export functionality for reports and analytics
