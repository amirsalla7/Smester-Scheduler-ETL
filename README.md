## Semester Scheduling Generator

## Project Overview

Semester Scheduling Generator is an automated scheduling system designed to generate university semester timetables based on academic rules and constraints.

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
- Automatic Excel file generation

---

## Technologies Used

- Python
- SQL Server
- ETL Pipeline
- Rule-Based Scheduling
- Constraint-Based Validation
- GitHub version control
- openpyxl (Excel file generation)

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
├── export_excel.py
├── config.json
├── requirements.txt
└── schedule.xlsx

---

## How the System Works

1. Data is extracted from the university system using API.
2. ETL process cleans and transforms the data.
3. Data is stored in SQL Server database.
4. Scheduling engine analyzes:
   - students
   - courses
   - instructors
   - classrooms
   - time slots
5. Conflict detection rules are applied.
6. Final schedule is generated.
7. Schedule is saved in database.
8. Excel file is created automatically.

---

## Scheduling Flow

Student Data  
↓  
Course Offering  
↓  
Instructor Load Check  
↓  
Scheduling Algorithm  
↓  
Conflict Resolution  
↓  
Save to Database  
↓  
Export Excel File  

---

## Output

The system generates:

- Conflict-free semester schedule
- Instructor teaching assignments
- Classroom allocation plan
- Time slot distribution
- Excel file containing the final schedule

Generated file:

schedule.xlsx

Location:

Same project folder.

---

## Algorithm Type

Rule-based scheduling with constraint validation.

The system ensures:

- No instructor time conflict
- No classroom double booking
- Teaching load does not exceed allowed limits
- Courses are assigned based on demand
- Time slots are distributed efficiently

---

## Installation

Install required Python libraries:

pip install -r requirements.txt

Libraries used:

requests  
pandas  
numpy  
pyodbc  
openpyxl  

---

## Run the Project

Run the scheduling system:

python main.py

The system will:

1. Run ETL process
2. Load cleaned data
3. Generate semester schedule
4. Store schedule in database
5. Create Excel file automatically

---

## Excel Output

After generating the schedule, the system automatically creates:

schedule.xlsx

The file contains:

Course  
Instructor  
Room  
Day  
Start time  
End time  

Example:

Database Systems | Dr. Ahmad | Room 101 | Sunday | 08:00 | 09:30  

---

## Future Work

- AI-based optimization algorithm
- Web interface
- Multi-semester planning
- Student-specific schedule generation
- Integration with LMS systems
- PDF export
- Real-time schedule updates
- Performance optimization for large datasets

---

## Authors

Amir Salah  
Omar Alnaimat  

Faculty of Information Technology  
Aqaba University of Technology  

Winter 2025–2026