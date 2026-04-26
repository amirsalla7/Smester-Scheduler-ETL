# Semester Scheduling Generator

## Project Overview

**Semester Scheduling Generator** is an automated academic scheduling system designed to generate university semester timetables based on student demand, academic constraints, and institutional rules.

The system integrates:

- ETL pipeline
- SQL Server database
- rule-based scheduling engine
- constraint validation
- PDF export
- Web-based UI (Python Eel)
- login authentication
- live schedule editing
- data export API

to automatically produce conflict-free schedules for:

- Courses
- Instructors
- Classrooms
- Time slots

The main goal of the system is to:

- reduce manual scheduling effort
- avoid scheduling conflicts
- ensure fair instructor workload distribution
- open courses based on real student demand
- prioritize graduating students
- improve academic planning efficiency

---

## Main Features

### Login Interface
- simple login screen
- username and password verification
- no database required for authentication

### Data Processing
- API-based data extraction
- ETL pipeline for cleaning and transformation
- flexible mapping system for handling different data formats
- dynamic field normalization using config.json
- on-the-fly data processing

### Student Analysis
- analyzes student academic progress
- determines course demand
- identifies near-graduation students (remaining hours ≤ threshold)
- prioritizes graduating students when opening courses
- force-opens courses if at least 1 graduating student needs them

### Course Offering Logic
courses are opened only when demand exists

rules:

- minimum 5 students required to open a course
- graduating student demand can force-open a course even below threshold
- prerequisite validation
- automatic course demand calculation

### Intelligent Scheduling
automatic assignment of:

- instructor
- room
- time slot

constraints enforced:

- no instructor time conflict
- no room double booking
- instructor load limit respected (by degree type)
- valid lecture time window
- section 2 prefers same instructor as section 1 (not forced)
- conflict-free timetable generation

allowed lecture time:

08:00 → 16:00

day patterns:

- Sun/Tue
- Mon/Wed
- Sun/Tue/Thu

### Web UI (Python Eel)
browser-based interface with:

- dashboard with live stats
- schedule viewer and editor
- manual schedule editing with conflict detection
- save edited schedule back to database
- PDF export with cache-busting
- conflict panel showing all violations

### Data Export API
`data_exporter.py` — standalone file, three modes:

| Mode | Command | Use case |
|------|---------|----------|
| Export files | `python data_exporter.py export` | Send JSON + Excel to friend via USB/email/cloud |
| LAN server | `python data_exporter.py serve` | Friend on same Wi-Fi connects to local API |
| Public tunnel | `python data_exporter.py tunnel` | Friend anywhere in world gets public HTTPS URL |

endpoints served:

- `/api/schedule` — full schedule with room and instructor names
- `/api/students` — all students
- `/api/courses` — all courses
- `/api/instructors` — all instructors
- `/api/rooms` — all rooms
- `/api/all` — everything in one response

### System Output
- conflict-free semester schedule
- instructor teaching assignments
- classroom allocation
- time slot distribution
- PDF file generation (schedule + summary report)
- database storage of generated schedule
- JSON and Excel export files

---

## Technologies Used

### Programming Languages
Python

### Database
SQL Server
pyodbc (ODBC Driver 17)

### Data Processing
ETL pipeline
JSON mapping engine

### Scheduling Approach
rule-based scheduling
constraint-based validation
graduating student priority

### Libraries
requests
pyodbc
reportlab (PDF generation)
Flask + flask-cors (data export API)
pyngrok (public tunnel)
openpyxl (Excel export)
eel (web UI bridge)

### UI
Python Eel + HTML/CSS/JavaScript

### Version Control
GitHub

---

## Project Structure

```
ssg/
├── main.py                  ← CLI entry point
├── web_app.py               ← Web UI entry point (Eel)
├── data_exporter.py         ← Standalone data export + API server
├── scheduler_engine.py      ← Core scheduling algorithm
├── scheduler_config.py      ← All configuration constants
├── student_analysis.py      ← Student graduation analysis
├── course_offering.py       ← Course opening decision logic
├── etl.py                   ← ETL pipeline (extract, transform, load)
├── mapping_engine.py        ← Flexible field mapping from config
├── db.py                    ← SQL Server connection helpers
├── exporter.py              ← PDF generation
├── student_summary.py       ← Summary report builder
├── web/
│   ├── index.html           ← Main UI page
│   ├── config.json          ← ETL field mapping config
│   ├── schedule.json        ← Last generated schedule
│   ├── report.json          ← Last summary report
│   ├── stats.json           ← Last run statistics
│   └── js/
│       ├── app.js           ← App state, login/logout
│       ├── pipeline.js      ← Run pipeline, load data
│       ├── schedule.js      ← Schedule table, editing, save bar
│       ├── report.js        ← Summary report view
│       ├── dashboard.js     ← Stats dashboard
│       └── ui.js            ← Shared UI helpers, PDF open
└── exports/                 ← Generated export files (git-ignored)
```

---

## Database Schema (Main Tables)

| Table | Description |
|-------|-------------|
| college | College information |
| department | Departments |
| major | Academic majors |
| plan | Study plan (total hours per major) |
| course | Courses with prerequisites |
| std | Students |
| std_course | Student course history (grades, status) |
| instructor | Instructors with degree and specialization |
| room | Rooms with capacity and type |
| time_slot | Available time slots per day |
| semester | Semesters |
| schedule | Generated schedule output |

---

## How the System Works

### Step 1 — Login
User enters username and password in the web UI login screen.

---

### Step 2 — Data Extraction
Data is retrieved from university systems using API or read directly from SQL Server.

---

### Step 3 — ETL Processing
Data is transformed and normalized using:

`mapping_engine.py` + `web/config.json`

config.json allows multiple possible field names. Example:

`student_id`, `std_id`, `id` → treated as the same field.

---

### Step 4 — Student Analysis
the system analyzes per student:

- completed courses and hours
- remaining hours to graduation
- prerequisite completion
- course demand contribution
- graduating status (remaining ≤ threshold, default 21h)

---

### Step 5 — Course Offering Decision

courses open if:
- total demand ≥ 5 students, **or**
- at least 1 graduating student needs it

---

### Step 6 — Scheduling Engine

scheduler assigns for each section:

`course → instructor → room → time slot`

constraints:

- instructor cannot teach two courses at same time
- room cannot host two courses at same time
- instructor load must not exceed degree-type limit
- courses with multiple sections use different day patterns
- section 2 prefers same instructor as section 1

load limits by degree:

| Degree | Max hours/semester |
|--------|--------------------|
| Professor | 9 |
| Associate Professor | 12 |
| Assistant Professor | 12 |
| Master | 15 |
| Doctor | 15 |

---

### Step 7 — Save Schedule
generated schedule stored in `schedule` table in SQL Server.

---

### Step 8 — PDF Export
system generates two PDFs:

- `semester_schedule.pdf` — full timetable
- `summary_report.pdf` — demand and coverage summary

---

### Step 9 — Manual Editing
user can edit the schedule in the web UI:

- change instructor, room, day, time for any row
- save bar appears after edits
- conflict detection runs before saving
- PDFs regenerated automatically after clean save

---

## Scheduling Flow

```
Login
↓
Load data from SQL Server
↓
Student Analysis (graduation detection)
↓
Course Demand Calculation
↓
Course Offering Decision (with graduating force-open)
↓
Sort courses by graduating demand (priority scheduling)
↓
For each course → assign instructor → assign room → assign time slot
↓
Conflict check (instructor + room)
↓
Save to Database
↓
Export PDF
```

---

## Data Export (data_exporter.py)

Export all data to files:
```bash
python data_exporter.py export
```
Creates `exports/` folder with JSON files + timestamped Excel workbook.

Run local API server (same Wi-Fi):
```bash
python data_exporter.py serve
```

Run public tunnel (friend anywhere):
```bash
python data_exporter.py tunnel
```
Prints a public HTTPS URL. Keep terminal open while friend is using it.

---

## Installation

install required libraries:

```bash
pip install -r requirements.txt
```

requirements:

```
requests
pyodbc
reportlab
eel
flask
flask-cors
pyngrok
openpyxl
```

configure database connection in `scheduler_config.py`:

```python
SERVER   = "localhost"
DATABASE = "master"
DRIVER   = "ODBC Driver 17 for SQL Server"
USE_TRUSTED_CONNECTION = True
```

---

## Run the Project

### Web UI (recommended)
```bash
python web_app.py
```

### CLI
```bash
python main.py
```

### Data Export
```bash
python data_exporter.py export    # files
python data_exporter.py serve     # LAN API
python data_exporter.py tunnel    # public URL
```

---

## Example Output (PDF)

| Course | Instructor | Room | Day | Start | End |
|--------|-----------|------|-----|-------|-----|
| AI Ethics | Dr. Ahmed Salem | A101 | Sun/Tue | 08:00 | 09:00 |
| Database Systems | Dr. Lina Khaled | B203 | Mon/Wed | 10:00 | 11:00 |

---

## Future Improvements

- AI-based optimization algorithm
- machine learning demand prediction
- multi-semester planning
- student-specific schedules
- Moodle integration
- real-time schedule updates
- OR-Tools optimization solver
- mobile app

---

## Authors

Amir Salah
Omar Alnaimat

Faculty of Information Technology
Aqaba University of Technology

Winter 2025–2026
