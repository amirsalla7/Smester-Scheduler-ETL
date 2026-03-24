CREATE DATABASE UniversityDB;
GO
USE UniversityDB;

-- College
CREATE TABLE collage (
    collage_id INT PRIMARY KEY,
    collage_na NVARCHAR(100)
);

-- Department
CREATE TABLE department (
    department_id INT PRIMARY KEY,
    department_na NVARCHAR(100),
    collage_id INT,
    FOREIGN KEY (collage_id) REFERENCES collage(collage_id)
);

-- Major
CREATE TABLE major (
    major_id INT PRIMARY KEY,
    major_na NVARCHAR(100),
    credit_hours INT,
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES department(department_id)
);

-- Student
CREATE TABLE std (
    std_id INT PRIMARY KEY,
    std_na NVARCHAR(100),
    major_id INT,
    FOREIGN KEY (major_id) REFERENCES major(major_id)
);

-- Instructor
CREATE TABLE instructor (
    instructor_id INT PRIMARY KEY,
    instructor_name NVARCHAR(100),
    spec NVARCHAR(100),
    degree_type NVARCHAR(50)
);

-- Course
CREATE TABLE course (
    course_id INT PRIMARY KEY,
    course_na NVARCHAR(100),
    credit_hours INT,
    type NVARCHAR(50),
    major_id INT,
    plan_id INT,
    prereq_id INT
);

-- Room
CREATE TABLE room (
    room_id INT PRIMARY KEY,
    building NVARCHAR(50),
    capacity INT,
    type NVARCHAR(50)
);

-- Time Slot
CREATE TABLE time_slot (
    time_id INT PRIMARY KEY,
    day NVARCHAR(20),
    s_time TIME,
    e_time TIME
);

-- Semester
CREATE TABLE semester (
    semester_id INT PRIMARY KEY,
    name NVARCHAR(50),
    s_date DATE,
    e_date DATE,
    status NVARCHAR(20)
);

-- Schedule
CREATE TABLE schedule (
    schedule_id INT PRIMARY KEY,
    room_id INT,
    time_id INT,
    course_id INT,
    instructor_id INT
);