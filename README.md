# Semester Scheduling Generator

## Project Overview

**Semester Scheduling Generator (SSG)** is an automated academic scheduling system that generates conflict-free university semester timetables based on real student demand, academic constraints, and institutional rules.

The system pulls live data from an external API database, transforms and loads it into a local SQL Server database via an ETL pipeline, then runs a rule-based scheduling engine to assign courses, instructors, rooms, and time slots automatically.

**One button does everything** — sync data, analyze students, build course offerings, generate schedule, export PDFs.

---

## Main Features

### Login
- Username and password login screen
- SHA-256 password hashing
- Credentials configured in `web_app.py`

### One-Click Pipeline
Clicking **Run Full Pipeline** automatically:
1. Syncs latest data from API database via ETL
2. Loads all data from local SQL Server
3. Analyzes student graduation status
4. Calculates course demand
5. Decides which courses to open
6. Generates conflict-free schedule
7. Exports PDF schedule and summary report

### Student Analysis
- Determines completed credit hours per student
- Calculates remaining hours to graduation
- Flags graduating students (remaining ≤ 21 hours)
- Builds course demand per student based on prerequisites

### Course Offering Logic
- Minimum 5 students required to open a course
- If at least 1 graduating student needs a course → force-open regardless of demand
- Prerequisite validation enforced
- Number of sections calculated from demand vs room capacity

### Scheduling Engine (Rule-Based)
Assigns for each section: `course → instructor → room → time slot`

Constraints enforced:
- No instructor double-booking
- No room double-booking
- Instructor load limit respected by degree type
- Teaching hours: 08:00 – 16:00 only
- Day patterns: Sun/Tue or Mon/Wed
- Multiple sections of same course must use different day patterns
- Section 2 prefers same instructor as section 1

Load limits:

| Degree | Max Credit Hours/Semester |
|--------|--------------------------|
| Professor | 9 |
| Associate Professor | 12 |
| Assistant Professor | 12 |
| Master | 15 |
| Doctor | 15 |

### Web UI (Python Eel)
- Dashboard with live stats (students, sections, conflicts)
- Schedule viewer with full table
- Inline schedule editing (instructor, room, day, time)
- Save bar with live conflict detection
- Conflict panel showing all violations
- PDF download for schedule and summary report

### Data Export API
`data_exporter.py` — three modes:

| Mode | Command | Use case |
|------|---------|----------|
| Export files | `python data_exporter.py export` | JSON + Excel files |
| LAN server | `python data_exporter.py serve` | Friend on same Wi-Fi |
| Public tunnel | `python data_exporter.py tunnel` | Friend anywhere via HTTPS |

Endpoints:
- `/api/schedule` `/api/students` `/api/courses`
- `/api/instructors` `/api/rooms` `/api/all`
- `/api/majors` `/api/departments` `/api/collages`
- `/api/plans` `/api/time_slots` `/api/semesters` `/api/std_course`

---

## Technologies

| Layer | Technology |
|-------|-----------|
| Language | Python 3 |
| Database | SQL Server + pyodbc (ODBC Driver 17) |
| Web UI | Python Eel + HTML / CSS / JavaScript |
| Scheduling | Rule-based engine (custom) |
| PDF Export | ReportLab |
| Data API | Flask + flask-cors |
| Public Tunnel | pyngrok |
| Excel Export | openpyxl |
| Version Control | GitHub |

---

## Project Structure

```
ssg/
├── web_app.py               ← Web UI entry point (Eel) + eel-exposed functions
├── data_exporter.py         ← Standalone data export + API server
├── scheduler_engine.py      ← Core rule-based scheduling engine
├── scheduler_config.py      ← All configuration constants
├── student_analysis.py      ← Student graduation analysis
├── course_offering.py       ← Course opening decision logic
├── etl.py                   ← ETL pipeline (fetch API → transform → load DB)
├── mapping_engine.py        ← Flexible field mapping from config.json
├── db.py                    ← SQL Server connection helpers
├── exporter.py              ← PDF generation (schedule + summary)
├── student_summary.py       ← Summary report builder
├── database_schema.sql      ← Full database schema (USE UniversityDB)
├── data.sql                 ← Test data (300 students, 21 courses, 9 instructors)
├── web/
│   ├── index.html           ← Main UI page (all pages in one file)
│   ├── config.json          ← ETL field mapping config
│   ├── schedule.json        ← Last generated schedule (auto-generated)
│   ├── report.json          ← Last summary report (auto-generated)
│   ├── stats.json           ← Last run statistics (auto-generated)
│   └── js/
│       ├── config.js        ← App config + pipeline step definitions
│       ├── app.js           ← App state, login/logout, page routing
│       ├── pipeline.js      ← Run pipeline, save edits, load data
│       ├── schedule.js      ← Schedule table, inline editing, save bar
│       ├── report.js        ← Summary report view
│       ├── dashboard.js     ← Stats dashboard rendering
│       ├── analytics.js     ← Charts and analytics
│       └── ui.js            ← Shared UI helpers, toast, PDF open
└── exports/                 ← Generated export files (git-ignored)
```

---

## Database Schema

| Table | Description |
|-------|-------------|
| `collage` | College information |
| `department` | Departments under each college |
| `major` | Academic majors with total credit hours |
| `[plan]` | Study plan per major |
| `course` | Courses with prerequisites and credit hours |
| `std` | Students with major assignment |
| `std_course` | Student course history (garde, status, section) |
| `instructor` | Instructors with degree type and specialization |
| `room` | Rooms with capacity and type |
| `time_slot` | Available time slots (day, start, end) |
| `semester` | Semester records |
| `schedule` | Generated schedule output |

---

## How the System Works

```
① Login
↓
② Click "Run Full Pipeline"
↓
③ ETL — fetch latest data from API → load into local SQL Server
↓
④ Load all tables (students, courses, instructors, rooms, time slots)
↓
⑤ Student Analysis — calculate completed hours, flag graduating students
↓
⑥ Course Demand — count eligible students per course (prereq check)
↓
⑦ Course Offering — decide which courses open + how many sections
↓
⑧ Scheduling Engine — assign instructor + room + time slot per section
↓
⑨ Conflict Validation — check room and instructor overlaps
↓
⑩ Save schedule.json, report.json, stats.json
↓
⑪ Export semester_schedule.pdf + summary_report.pdf
↓
⑫ UI refreshes with new data
```

---

## Installation

```bash
pip install -r requirements.txt
```

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

Configure database connection in `scheduler_config.py`:

```python
SERVER   = "localhost"
DATABASE = "UniversityDB"
DRIVER   = "ODBC Driver 17 for SQL Server"
USE_TRUSTED_CONNECTION = True
```

Set the API URL (where your source database is exposed):

```python
API_BASE_URL = "http://127.0.0.1:5000"
```

---

## Run the Project

```bash
# Start the web app
python web_app.py

# Export data to files
python data_exporter.py export

# Share data via LAN
python data_exporter.py serve

# Share data via public URL
python data_exporter.py tunnel
```

---

## Test Data

`data.sql` contains a ready-to-run test dataset:

| | Count |
|-|-------|
| Students | 300 |
| Graduating students | 120 |
| Non-graduating students | 180 |
| Courses | 21 (7 per major) |
| Instructors | 9 (3 per major) |
| Rooms | 8 (5 lecture + 3 lab) |
| Time slots | 40 (08:00–16:00, all days) |
| Majors | 3 (AI, SE, CY) |

---

## Bugs Fixed During Development

| Bug | Fix |
|-----|-----|
| `garde` column referenced as `grade` in SQL queries | Fixed column alias across all Python files |
| Graduating student hours logic error | Fixed remaining-hours calculation |
| Section 2 never scheduled | Fixed loop in scheduler engine |
| PDF file locked on Windows | Write to temp file then rename |
| ETL path error on different working directory | Fixed using `os.path.dirname(__file__)` |
| SQL reserved keyword `plan` causing query failure | Wrapped in `[plan]` brackets |

---

## Future Work

- Role-based login for instructors and admins
- Configurable scheduling rules from the UI
- Exam and final assessment scheduling
- Multi-semester planning
- Standalone web application (replace Eel)
- Automatic instructor notifications

---

## Authors

Amir Salah
Omar Alnaimat

Faculty of Information Technology
Aqaba University of Technology

Winter 2025–2026
