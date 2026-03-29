# Semester Scheduling Generator

## Project Overview

**Semester Scheduling Generator** is an automated academic scheduling system designed to generate university semester timetables based on student demand, academic constraints, and institutional rules.

The system integrates:

- ETL pipeline
- SQL Server database
- rule-based scheduling engine
- constraint validation
- PDF export
- C# user interface trigger

to automatically produce conflict-free schedules for:

- Courses
- Instructors
- Classrooms
- Time slots

The main goal of the system is to:

- reduce manual scheduling effort
- avoid conflicts
- ensure fair instructor load distribution
- open courses based on real student demand
- improve academic planning efficiency

---

## Main Features

### Data Processing
- API-based data extraction
- ETL pipeline for cleaning and transformation
- Flexible mapping system for handling different data formats
- On-the-fly data processing (lazy loading)

### Intelligent Scheduling
- Automatic course offering based on student demand
- Minimum student threshold for opening courses
- Priority handling for near-graduation students
- Instructor teaching load constraints
- Classroom capacity validation
- Time slot allocation
- Conflict detection and prevention

### System Output
- conflict-free semester schedule
- instructor teaching assignments
- classroom allocation
- time slot distribution
- PDF file generation
- database storage of generated schedule

### Interface
- C# Windows Form button to run scheduling system
- one-click execution workflow

---

## Technologies Used

### Programming
- Python
- C#

### Database
- SQL Server
- pyodbc

### Data Processing
- ETL pipeline
- JSON mapping engine

### Scheduling Approach
- rule-based scheduling
- constraint-based validation

### Libraries
- requests
- pyodbc
- reportlab (PDF generation)

### Tools
- GitHub version control

---

## Project Structure

Semester-Scheduling-Generator/
│
├── etl.py
├── mapping_engine.py
├── scheduler_engine.py
├── scheduler_config.py
├── db.py
├── main.py
├── exporter.py
├── student_analysis.py
├── course_offering.py
├── config.json
├── requirements.txt
│
├── SchedulerUI/
│   ├── Form1.cs
│   ├── Program.cs
│
└── semester_schedule.pdf

---

## Database Schema (Main Tables)

- college
- department
- major
- plan
- course
- std
- std_course
- instructor
- room
- time_slot
- semester
- schedule

---

## How the System Works

### Step 1 — Data Extraction
Data is retrieved from university systems using API.

### Step 2 — ETL Processing
Data is transformed and normalized using:

mapping_engine.py

The system supports multiple possible field names using config.json mapping.

Example:

student_id  
std_id  
id  

are treated as the same field.

---

### Step 3 — Data Storage
Cleaned data is stored in SQL Server database:

UniversityDB

---

### Step 4 — Student Analysis
The system analyzes:

- completed courses
- failed courses
- missing courses
- course demand
- graduation priority

Table used:

std_course

---

### Step 5 — Course Offering Decision

Courses are opened only if demand meets threshold.

Example rule:

Course opens if total students ≥ 5

This ensures resources are used efficiently.

---

### Step 6 — Scheduling Engine

Scheduler assigns:

Course → Instructor → Room → Time slot

Constraints enforced:

- no instructor time conflict
- no room double booking
- instructor load limit respected
- room capacity sufficient
- allowed lecture time window
- conflict-free timetable generation

Allowed lecture time:

08:00 → 16:00

---

### Step 7 — Save Schedule

Generated schedule is saved to:

schedule table

---

### Step 8 — PDF Export

The system automatically generates:

semester_schedule.pdf

The file contains:

- course
- instructor
- room
- day
- start time
- end time
- credit hours

Example:

Database Systems | Dr. Ahmad | Room 101 | Sunday | 08:00 | 09:30

---

## Scheduling Flow

Student Data  
↓  
Student Analysis  
↓  
Course Demand Calculation  
↓  
Course Offering Decision  
↓  
Instructor Load Check  
↓  
Room Allocation  
↓  
Time Slot Assignment  
↓  
Conflict Resolution  
↓  
Save to Database  
↓  
Export PDF  

---

## Output

The system generates:

- conflict-free semester schedule
- instructor teaching assignments
- classroom allocation plan
- time slot distribution
- PDF schedule file

Generated file:

semester_schedule.pdf

Location:

project root folder

---

## Algorithm Type

Rule-based scheduling with constraint validation.

The system ensures:

- instructor availability respected
- classroom conflicts prevented
- teaching load limits enforced
- courses opened based on demand
- time slots distributed efficiently

---

## Installation

Install required libraries:

pip install -r requirements.txt

requirements.txt:

requests  
pyodbc  
reportlab  

---

## Run the Project

Run from Python:

python main.py

Or using C# interface:

Click:

Generate Schedule

The system will:

1. run ETL process
2. load cleaned data
3. analyze student demand
4. decide course offerings
5. generate semester schedule
6. store schedule in database
7. create PDF file automatically

---

## Example Output (PDF)

Course | Instructor | Room | Day | Start | End
-------|-----------|------|-----|-------|----
AI | Dr. Ahmad | A101 | Sunday | 08:00 | 09:30
DB | Dr. Lina | B203 | Monday | 10:00 | 11:30

---

## Future Improvements

- AI optimization algorithm
- machine learning demand prediction
- multi-semester planning
- student-specific schedules
- web interface
- Moodle integration
- real-time schedule updates
- OR-Tools optimization solver
- performance optimization for large universities

---

## Authors

Amir Salah  
Omar Alnaimat  

Faculty of Information Technology  
Aqaba University of Technology  

Winter 2025–2026