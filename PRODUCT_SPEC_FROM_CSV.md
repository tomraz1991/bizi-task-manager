# Podcast Task Manager - Product Specification

## Extracted from Hebrew Google Sheet (base.csv)

---

## 1. Entities

### 1.1 Podcast

A podcast show that can have multiple episodes.

**Key Characteristics:**

- Each podcast has a unique name (in Hebrew)
- Some podcasts have an associated host/producer (stored in first column when present)
- Examples: "רוני וברק", "סטימצקי", "אפרת וכטל", "נטע פיזיותרפיה", "מנהלי שיווק מצייצים"

### 1.2 Episode

A single episode of a podcast, representing one recording/production unit.

**Key Characteristics:**

- Belongs to one podcast
- Can have an episode number (numeric, text, or season-based like "עונה 3 פרק 1")
- Can be a regular episode or a "reels" episode (short-form content)
- Can be a "pilot" episode
- Tracks production workflow from recording to publishing
- Has assigned recording engineer (הקלטה), editing engineer (עריכה), and reels engineer
- Each engineer assignment is optional and independent

### 1.3 Studio

A physical location where recordings take place.

**Key Characteristics:**

- Episodes are recorded at specific studios
- Examples from data: "שמונאים", "גבעון", "TLV", "ביפו"
- Some episodes may not have a studio assigned

### 1.4 Guest

A person featured in an episode.

**Key Characteristics:**

- Multiple guests can appear in a single episode
- Guest names are stored as free-form text
- Some episodes have no guests (host-only episodes)

### 1.5 Team Member (User)

A person assigned to production tasks.

**Key Characteristics:**

- Can be assigned to different task types (recording, editing, reels)
- Multiple team members can work on the same episode
- Examples from data: "אורי", "אלי", "בניה", "גאיה", "שחר", "יובל", "ליאור", "עדי", "יותם", "איתי", "יובל", "בניה"

### 1.6 Storage Card

A storage device or task board identifier for organizing work.

**Key Characteristics:**

- Used to group related episodes/tasks
- Can be podcast name in transliterated form (e.g., "roni ve barak", "stimatsky")
- Can be storage device name (e.g., "SSDzilla", "KONG 3", "TERRA 1", "WD 500G", "KINGSTON 2", "מק לובי")
- Some entries use "---" or are empty

### 1.7 Task

A work item associated with an episode. Each episode has three potential task types.

**Key Characteristics:**

- Recording task (הקלטה)
- Editing task (עריכה)
- Reels task (reels)
- Each task can have a different assigned team member
- Tasks are tracked independently

---

## 2. Fields

### 2.1 Podcast Fields

| Field Name   | Type     | Required | Description                | Example        |
| ------------ | -------- | -------- | -------------------------- | -------------- |
| `id`         | Integer  | Yes      | Unique identifier          | Auto-generated |
| `name`       | String   | Yes      | Podcast name in Hebrew     | "רוני וברק"    |
| `host`       | String   | No       | Primary host/producer name | "אבי זייתן"    |
| `created_at` | DateTime | Yes      | Creation timestamp         | Auto-generated |
| `updated_at` | DateTime | Yes      | Last update timestamp      | Auto-updated   |

### 2.2 Episode Fields

| Field Name              | Type     | Required | Description                                | Example                                    |
| ----------------------- | -------- | -------- | ------------------------------------------ | ------------------------------------------ |
| `id`                    | Integer  | Yes      | Unique identifier                          | Auto-generated                             |
| `podcast_id`            | Integer  | Yes      | Reference to podcast                       | Foreign key                                |
| `episode_number`        | String   | No       | Episode identifier                         | "33", "עונה 3 פרק 1", "רילז - 2", "פיילוט" |
| `recording_date`        | Date     | No       | Date when episode was recorded             | "15.1.25", "30.1.25", "17.2.25"            |
| `studio`                | String   | No       | Studio location name                       | "שמונאים", "גבעון", "TLV"                  |
| `guest_names`           | String   | No       | Comma-separated guest names                | "חנה ראדו", "דניאל ויעל"                   |
| `status`                | Enum     | Yes      | Overall episode status                     | See Status Values below                    |
| `episode_notes`         | Text     | No       | Free-form notes about episode              | "יבואו להקליט רילז", "לתקן שטיח מוסיקלי"   |
| `drive_link`            | String   | No       | Google Drive link to files                 | URL                                        |
| `backup_deletion_date`  | Date     | No       | Date when deleted from backup              | "7.2.25"                                   |
| `card_name`             | String   | No       | Storage card/task board identifier         | "roni ve barak", "SSDzilla"                |
| `recording_engineer_id` | Integer  | No       | Engineer responsible for recording (הקלטה) | Foreign key to User                        |
| `editing_engineer_id`   | Integer  | No       | Engineer responsible for editing (עריכה)   | Foreign key to User                        |
| `reels_engineer_id`     | Integer  | No       | Engineer responsible for reels extraction  | Foreign key to User                        |
| `created_at`            | DateTime | Yes      | Creation timestamp                         | Auto-generated                             |
| `updated_at`            | DateTime | Yes      | Last update timestamp                      | Auto-updated                               |

### 2.3 Task Fields

| Field Name    | Type     | Required | Description            | Example                              |
| ------------- | -------- | -------- | ---------------------- | ------------------------------------ |
| `id`          | Integer  | Yes      | Unique identifier      | Auto-generated                       |
| `episode_id`  | Integer  | Yes      | Reference to episode   | Foreign key                          |
| `type`        | Enum     | Yes      | Task type              | "recording", "editing", "reels"      |
| `assigned_to` | Integer  | No       | Team member user ID    | Foreign key to User                  |
| `notes`       | Text     | No       | Task-specific notes    | "עריכה מול נסטיה!"                   |
| `status`      | Enum     | Yes      | Task completion status | "not_started", "in_progress", "done" |
| `created_at`  | DateTime | Yes      | Creation timestamp     | Auto-generated                       |
| `updated_at`  | DateTime | Yes      | Last update timestamp  | Auto-updated                         |

### 2.4 User Fields

| Field Name   | Type     | Required | Description           | Example               |
| ------------ | -------- | -------- | --------------------- | --------------------- |
| `id`         | Integer  | Yes      | Unique identifier     | Auto-generated        |
| `name`       | String   | Yes      | User's name in Hebrew | "אורי", "גאיה", "שחר" |
| `email`      | String   | No       | Email address         | Optional              |
| `created_at` | DateTime | Yes      | Creation timestamp    | Auto-generated        |
| `updated_at` | DateTime | Yes      | Last update timestamp | Auto-updated          |

### 2.5 Studio Fields (if modeled as entity)

| Field Name   | Type     | Required | Description        | Example            |
| ------------ | -------- | -------- | ------------------ | ------------------ |
| `id`         | Integer  | Yes      | Unique identifier  | Auto-generated     |
| `name`       | String   | Yes      | Studio name        | "שמונאים", "גבעון" |
| `location`   | String   | No       | Physical location  | Optional           |
| `created_at` | DateTime | Yes      | Creation timestamp | Auto-generated     |

---

## 3. Business Rules

### 3.1 Episode Status Values

The system uses the following status values (in Hebrew, stored as enum):

1. **"הוקלט"** (Recorded) - Episode has been recorded but not yet edited
2. **"בעריכה"** (In Editing) - Episode is currently being edited
3. **"הופץ"** (Published) - Episode has been published/released
4. **"נשלח ללקוח"** (Sent to Client) - Episode has been sent to client for review/approval
5. **"לא התחילה"** (Not Started) - Recording has not begun

### 3.2 Status Progression Rules

1. **Typical Workflow**: Not Started → Recorded → In Editing → Sent to Client → Published
2. **Status can skip steps**: An episode can go directly from "Recorded" to "Published" without "In Editing" or "Sent to Client"
3. **Status can regress**: An episode can move backwards (e.g., from "In Editing" back to "Recorded" if re-recording is needed)
4. **Multiple statuses per podcast**: Different episodes of the same podcast can be at different statuses simultaneously

### 3.3 Engineer Assignment Rules

1. **Episode-level assignments**:

   - Each episode has three engineer assignment fields: `recording_engineer_id`, `editing_engineer_id`, and `reels_engineer_id`
   - These are direct fields on the Episode entity, not separate task entities
   - Each assignment references a User (team member)

2. **Multiple assignments per episode**:

   - Recording, editing, and reels can each have different assigned engineers
   - Example: Recording by "אלי", Editing by "גאיה", Reels by "שחר"

3. **Optional assignments**:

   - Not all episodes have all three engineers assigned
   - Reels engineer is optional (many episodes don't have reels)
   - Recording and editing engineers are typically present but can be empty

4. **Same person multiple roles**:

   - One person can be assigned to multiple roles on the same episode
   - Example: "שחר" assigned to both editing and reels

5. **Assignment independence**:
   - Engineer assignments are independent of each other
   - An episode can have only a recording engineer, only an editing engineer, or any combination

### 3.4 Episode Number Rules

1. **Flexible format**: Episode numbers can be:

   - Numeric: "33", "1", "5"
   - Season-based: "עונה 3 פרק 1", "עונה 3 פרק 2"
   - Special identifiers: "רילז - 2", "פיילוט", "344/345"
   - Can be empty

2. **Reels episodes**: Some episodes are specifically for reels content and may have "רילז" in the episode number

3. **Pilot episodes**: Marked with "פיילוט" in episode number or notes

### 3.5 Recording Date Rules

1. **Date format**: Supports multiple formats:

   - DD.MM.YY: "15.1.25", "30.1.25"
   - DD/MM/YY: "27/05/25", "04/06/25"
   - DD.MM.YYYY: "5.3.2025", "6.3.2025"

2. **Optional field**: Recording date can be empty (future recordings or TBD)

3. **Date parsing**: System must handle all three date formats during import

### 3.6 Studio Rules

1. **Optional field**: Studio can be empty
2. **Multiple studios**: Different episodes can be recorded at different studios
3. **Studio names**: Stored as free-form text (Hebrew or English)

### 3.7 Guest Rules

1. **Multiple guests**: Guest names stored as comma-separated string
2. **Optional field**: Episodes can have no guests (host-only)
3. **Guest name format**: Free-form text, can include:
   - Single name: "חנה ראדו"
   - Multiple names: "דניאל ויעל", "אביב כהן ועדי בר לב"
   - Question marks for uncertainty: "עם מי ?", "שמות ?"

### 3.8 Storage Card Rules

1. **Card name purpose**: Used to organize episodes/tasks, often matches podcast name in transliterated form
2. **Storage device names**: Can also reference physical storage devices
3. **Special values**:
   - "---" indicates no card assigned
   - Empty string indicates no card assigned

### 3.9 Notes Rules

1. **Episode notes**: General notes about the episode (e.g., "יבואו להקליט רילז", "לתקן שטיח מוסיקלי")
2. **Reels notes**: Specific notes about reels content (e.g., "להוציא רילז", "השלמות לרילז יום כיפור")
3. **Task notes**: Can be stored at task level for task-specific information

### 3.10 Drive Link Rules

1. **Optional field**: Not all episodes have drive links
2. **Link format**: Google Drive URLs
3. **Purpose**: Provides access to episode files (audio, video, assets)

### 3.11 Backup Deletion Rules

1. **Optional field**: Date when episode was deleted from backup storage
2. **Format**: Date in DD.MM.YY format
3. **Purpose**: Tracks when files are removed from backup systems

### 3.12 Host/Producer Rules

1. **Optional field**: First column in CSV represents host/producer
2. **Not always present**: Many rows have empty first column
3. **Multiple hosts**: Some podcasts may have multiple hosts/producers
4. **Relationship**: Host is associated with podcast, not individual episodes

---

## 4. Views

### 4.1 Episode List View

**Purpose**: Display all episodes with key information

**Columns/Fields to Display:**

- Podcast name
- Episode number
- Recording date
- Studio
- Guest names
- Status
- Assigned team members (recording, editing, reels)
- Card name

**Filtering Options:**

- By podcast
- By status
- By studio
- By assigned team member
- By date range (recording date)
- By guest name (search)

**Sorting Options:**

- Recording date (newest/oldest first)
- Episode number
- Status
- Podcast name

### 4.2 Episode Detail View

**Purpose**: Show complete information for a single episode

**Sections:**

1. **Basic Information**

   - Podcast name
   - Episode number
   - Recording date
   - Studio
   - Guest names
   - Status
   - Card name

2. **Engineer Assignments**

   - Recording engineer (הקלטה) - name and link to user profile
   - Editing engineer (עריכה) - name and link to user profile
   - Reels engineer - name and link to user profile

3. **Notes Section**

   - Episode notes
   - Reels notes

4. **Links & Files**
   - Drive link
   - Backup deletion date

### 4.3 Task Board View (Kanban)

**Purpose**: Visualize tasks in workflow stages

**Columns:**

- Not Started
- In Progress (Recording)
- In Progress (Editing)
- In Progress (Reels)
- Completed
- Blocked

**Card Information:**

- Episode name (Podcast + Episode number)
- Task type
- Assigned team member
- Due date (if applicable)
- Status indicators

**Filtering:**

- By task type
- By assigned team member
- By podcast
- By status

### 4.4 Team Workload View

**Purpose**: Show episodes assigned to each engineer

**Layout:**

- List of team members (engineers)
- For each team member:
  - Episodes as recording engineer (count and list)
  - Episodes as editing engineer (count and list)
  - Episodes as reels engineer (count and list)
  - Total episodes assigned
  - Episodes by status breakdown

**Filtering:**

- By team member
- By role (recording, editing, reels)
- By episode status

### 4.5 Podcast Overview View

**Purpose**: Show all episodes for a specific podcast

**Information Displayed:**

- Podcast name and host
- List of all episodes with:
  - Episode number
  - Recording date
  - Status
  - Assigned team members
  - Guest names
- Statistics:
  - Total episodes
  - Episodes by status
  - Episodes in progress
  - Episodes published

**Filtering:**

- By status
- By date range

### 4.6 Studio Schedule View

**Purpose**: Show recording schedule by studio

**Layout:**

- List of studios
- For each studio:
  - Upcoming recordings (future dates)
  - Recent recordings (past dates)
  - Episodes in production

**Information per Episode:**

- Podcast name
- Episode number
- Recording date
- Guest names
- Status

### 4.7 Status Dashboard View

**Purpose**: High-level overview of production pipeline

**Metrics/Widgets:**

1. **Status Distribution**

   - Count of episodes by status
   - Visual chart (pie or bar)

2. **Tasks Overview**

   - Total tasks
   - Tasks by type (recording, editing, reels)
   - Tasks by status

3. **Team Workload**

   - Tasks per team member
   - Overdue tasks (if due dates implemented)

4. **Recent Activity**

   - Recently recorded episodes
   - Recently published episodes
   - Recently updated tasks

5. **Upcoming Recordings**
   - Episodes scheduled for recording (future dates)

### 4.8 Search View

**Purpose**: Find episodes, tasks, or information quickly

**Search Capabilities:**

- Search by podcast name
- Search by guest name
- Search by episode number
- Search by notes content
- Search by team member name
- Search by card name

**Results Display:**

- Matching episodes with key information
- Highlight matching terms
- Link to episode detail view

### 4.9 Reels Management View

**Purpose**: Focus on reels-specific tasks and content

**Information Displayed:**

- Episodes with reels tasks
- Reels task status
- Assigned team member for reels
- Reels notes
- Reels-specific episodes (episode number contains "רילז")

**Filtering:**

- By status
- By assigned team member
- Episodes with reels notes

### 4.10 Client Delivery View

**Purpose**: Track episodes sent to clients

**Information Displayed:**

- Episodes with status "נשלח ללקוח" (Sent to Client)
- Date sent (if tracked)
- Client name (if associated with podcast)
- Awaiting approval/feedback
- Drive links for client access

**Actions:**

- Mark as approved
- Mark as published (after client approval)
- Add client feedback/notes

---

## 5. Data Relationships

```
Podcast (1) ──< (many) Episode
                                    │
                                    ├──> User (via recording_engineer_id)
                                    ├──> User (via editing_engineer_id)
                                    └──> User (via reels_engineer_id)

Studio (1) ──< (many) Episode

Episode (many) ──< (many) Guest (stored as text, not normalized)

Episode (1) ──< (many) Task (optional, for additional task tracking)
                                    └──> User (via assigned_to)
```

---

## 6. Import/Export Specifications

### 6.1 CSV Import Format

The system must support importing from CSV with the following column structure:

| Column | Hebrew Header   | English Equivalent   | Type   | Required |
| ------ | --------------- | -------------------- | ------ | -------- |
| 1      | (empty)         | Host/Producer        | String | No       |
| 2      | שם הפודקאסט     | Podcast Name         | String | Yes      |
| 3      | תאריך הקלטה     | Recording Date       | Date   | No       |
| 4      | אולפן           | Studio               | String | No       |
| 5      | פרק מספר        | Episode Number       | String | No       |
| 6      | שם אורחים       | Guest Names          | String | No       |
| 7      | סטטוס           | Status               | Enum   | Yes      |
| 8      | הערות לפרק      | Episode Notes        | Text   | No       |
| 9      | על איזה כרטיס   | Card Name            | String | No       |
| 10     | הקלטה           | Recording Engineer   | String | No       |
| 11     | עריכה           | Editing Engineer     | String | No       |
| 12     | reels           | Reels Engineer       | String | No       |
| 13     | הערות לרילס     | Reels Notes          | Text   | No       |
| 14     | לינק לדרייב     | Drive Link           | String | No       |
| 15     | ת. מחיקה מגיבוי | Backup Deletion Date | Date   | No       |

### 6.2 Import Rules

1. **Podcast Creation**: Create podcast if name doesn't exist
2. **Episode Creation**: Create episode for each row
3. **Engineer Assignment**: Map columns 10, 11, 12 to episode engineer fields:
   - Column 10 (הקלטה) → `recording_engineer_id`
   - Column 11 (עריכה) → `editing_engineer_id`
   - Column 12 (reels) → `reels_engineer_id`
4. **User Creation**: Create users if engineer names in columns 10, 11, 12 don't exist, then link to episode engineer fields
5. **Date Parsing**: Handle multiple date formats (DD.MM.YY, DD/MM/YY, DD.MM.YYYY)
6. **Empty Values**: Treat empty strings as null/optional (engineer fields can be null)
7. **Special Values**: Handle "---" in card name as null

---

## 7. Additional Observations from Data

### 7.1 Common Patterns

1. **Reels Episodes**: Some episodes are specifically for reels (e.g., "רילז - 2", "2 רילז")
2. **Pilot Episodes**: Marked with "פיילוט" in episode number or notes
3. **Multiple Episodes Same Date**: Multiple episodes can be recorded on the same date
4. **Storage Device Tracking**: System tracks which storage device files are on (SSDzilla, KONG 3, TERRA 1, etc.)
5. **Client Projects**: Some podcasts appear to be client projects (e.g., "עופר - אדם, טבע ודין", "פארמה תמר")

### 7.2 Data Quality Notes

1. **Inconsistent Dates**: Mix of date formats requires robust parsing
2. **Missing Data**: Many fields are optional and frequently empty
3. **Uncertainty Markers**: Question marks in guest names indicate uncertainty
4. **Duplicate Rows**: Some episodes may appear multiple times (possibly different tasks or versions)

---

## 8. Future Considerations

1. **Normalize Guests**: Consider creating a Guest entity if guest tracking becomes more important
2. **Due Dates**: Add due date tracking for tasks
3. **Notifications**: Alert team members when tasks are assigned or status changes
4. **File Management**: Integrate with Google Drive API for automatic link validation
5. **Time Tracking**: Track time spent on tasks
6. **Version Control**: Handle multiple versions of episodes
7. **Client Portal**: Separate view for clients to review episodes
8. **Calendar Integration**: Sync recording dates with calendar systems
9. **Reporting**: Generate production reports (episodes per month, team productivity, etc.)
10. **Mobile Access**: Mobile-friendly interface for on-the-go updates
