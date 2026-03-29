## Semester-Scheduler

## Project Overview
 Semester Schedule Generator is an automated scheduling system designed to generate university semester timetables based on academic rules and constraints.

The system integrates ETL (Extract, Transform, Load) processes with a rule-based scheduling engine to produce conflict-free schedules for courses, instructors, classrooms, and time slots.

The goal of the system is to reduce manual effort, minimize scheduling conflicts, and improve academic planning efficiency.

---

## Main Features
- Automated semester schedule generation
- Conflict detection and resolution
- Instructor load management
- Classroom allocation
- Time slot assignment
- API-based data integration
- Flexible data mapping system
- On-the-fly data processing

---

## Technologies Used
- Python
- SQL Server
- ETL Pipeline
- Rule-Based Scheduling
- Constraint-Based Validation
- GitHub version control

---

## Project Structure

Semester-Scheduler

    etl.py
    mapping_engine.py
    scheduler_engine.py
    scheduler_config.py
    db.py
    config.json
    requirements.txt
    README.md

---

## How the System Works

1. Data is extracted from the university system via API.
2. Data is transformed and normalized using a mapping engine.
3. Cleaned data is loaded into SQL Server database.
4. Scheduling engine assigns:
   - instructors
   - classrooms
   - time slots
5. System checks constraints and resolves conflicts.
6. Final schedule is saved in the database.

---

## Algorithms Used
- Rule-Based Scheduling
- Constraint-Based Scheduling
- Priority-Based Assignment
- Greedy Allocation
- Conflict Detection and Resolution

---

## Installation

pip install -r requirements.txt

---

## Run the System

python etl.py

python main.py

---

## Future Work
- Student-level schedule generation
- AI-based optimization
- Automatic section creation
- Web interface
- Integration with LMS systems
- PDF schedule export

---

## Authors
Amir Salah
Omar Alnaimat

Faculty of Information Technology
Aqaba University of Technology