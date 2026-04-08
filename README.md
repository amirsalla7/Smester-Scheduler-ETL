# Semester Scheduling Generator

## Project Overview

**Semester Scheduling Generator** is an automated academic scheduling system designed to generate university semester timetables based on student demand, academic constraints, and institutional rules.

The system integrates:

- ETL pipeline
- SQL Server database
- rule-based scheduling engine
- constraint validation
- PDF export
- C# desktop interface
- login authentication
- progress tracking UI

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
- improve academic planning efficiency

---

## Main Features

### Login Interface
- simple login screen
- username and password verification inside application code
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
- identifies near-graduation students
- prioritizes students close to graduation

### Course Offering Logic
courses are opened only when demand exists

rules:

- minimum number of students required to open course
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
- instructor load limit respected
- valid lecture time window
- conflict-free timetable generation

allowed lecture time:

08:00 → 16:00

lab courses may contain:

0 practical hours if defined in study plan

### Progress Tracking UI
C# interface shows:

- execution progress bar
- real-time status messages
- one-click schedule generation

### System Output
- conflict-free semester schedule
- instructor teaching assignments
- classroom allocation
- time slot distribution
- PDF file generation
- database storage of generated schedule

---

## Technologies Used

### Programming Languages
Python
C#

### Database
SQL Server
pyodbc

### Data Processing
ETL pipeline
JSON mapping engine

### Scheduling Approach
rule-based scheduling
constraint-based validation

### Libraries
requests
pyodbc
reportlab (PDF generation)

### Desktop UI
Windows Forms

### Version Control
GitHub

---

## Project Structure

Semester-Scheduling-Generator/

Python Core
------------
etl.py
mapping_engine.py
scheduler_engine.py
scheduler_config.py
db.py
main.py
exporter.py
student_analysis.py
course_offering.py
config.json
requirements.txt

C# Desktop UI
--------------
SchedulerUI/
    Form1.cs
    LoginForm.cs
    Program.cs

Output
-------
semester_schedule.pdf

---

## Database Schema (Main Tables)

college
department
major
plan
course
std
std_course
instructor
room
time_slot
semester
schedule

---

## How the System Works

### Step 1 — Login
User enters username and password in C# login form.

If credentials are correct, the scheduling system starts.

---

### Step 2 — Data Extraction
Data is retrieved from university systems using API or database.

---

### Step 3 — ETL Processing
Data is transformed and normalized using:

mapping_engine.py

config.json allows multiple possible field names.

Example:

student_id
std_id
id

are treated as the same field.

---

### Step 4 — Data Storage
cleaned data stored in SQL Server database:

UniversityDB

---

### Step 5 — Student Analysis
the system analyzes:

- completed courses
- missing courses
- prerequisite completion
- course demand
- graduation priority

table used:

std_course

---

### Step 6 — Course Offering Decision

courses are opened only if demand meets threshold.

example rule:

course opens if total students ≥ 5

this ensures efficient resource usage.

---

### Step 7 — Scheduling Engine

scheduler assigns:

course → instructor → room → time slot

constraints enforced:

- instructor cannot teach two courses at same time
- room cannot host two courses at same time
- instructor load must not exceed allowed limit
- room capacity must be sufficient
- lecture time must be within allowed range
- no duplicate schedule entries

allowed lecture time window:

08:00 → 16:00

---

### Step 8 — Save Schedule

generated schedule stored in:

schedule table

---

### Step 9 — PDF Export

system automatically generates:

semester_schedule.pdf

PDF contains:

course id
course name
instructor name
room id
day
start time
end time
credit hours

---

### Step 10 — Progress Display

C# interface displays:

loading data
analyzing students
generating schedule
saving results
exporting PDF

---

## Scheduling Flow

Login
↓
Load data
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

the system generates:

- conflict-free semester schedule
- instructor teaching assignments
- classroom allocation plan
- time slot distribution
- PDF schedule file

generated file:

semester_schedule.pdf

location:

project root folder

---

## Algorithm Type

rule-based scheduling with constraint validation.

system ensures:

- instructor availability respected
- classroom conflicts prevented
- teaching load limits enforced
- courses opened based on demand
- time slots distributed efficiently

---

## Installation

install required libraries:

pip install -r requirements.txt

requirements:

requests
pyodbc
reportlab

---

## Run the Project

run using python:

python main.py

or using C# interface:

run application
login
click:

Generate Schedule

system will:

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

AI-based optimization algorithm
machine learning demand prediction
multi-semester planning
student-specific schedules
web interface
Moodle integration
real-time schedule updates
OR-Tools optimization solver
performance optimization for large universities

---

## Authors

Amir Salah
Omar Alnaimat

Faculty of Information Technology
Aqaba University of Technology

Winter 2025–2026