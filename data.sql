USE master;

------------------------------------------------
-- Clean old data (order matters: child → parent)
------------------------------------------------
DELETE FROM schedule;
DELETE FROM std_course;
DELETE FROM semester;
DELETE FROM time_slot;
DELETE FROM room;
DELETE FROM instructor;
DELETE FROM std;
DELETE FROM course;
DELETE FROM [plan];
DELETE FROM major;
DELETE FROM department;
DELETE FROM collage;

------------------------------------------------
-- College
------------------------------------------------
INSERT INTO collage (collage_id, collage_na) VALUES
(1, 'Faculty of Information Technology');

------------------------------------------------
-- Departments
------------------------------------------------
INSERT INTO department (department_id, department_na, collage_id) VALUES
(1, 'Artificial Intelligence', 1),
(2, 'Software Engineering',    1),
(3, 'Cyber Security',          1);

------------------------------------------------
-- Majors
-- credit_hours = 30 (10 courses x 3 hours each)
------------------------------------------------
INSERT INTO major (major_id, major_na, credit_hours, department_id) VALUES
(1, 'AI', 30, 1),
(2, 'SE', 30, 2),
(3, 'CY', 30, 3);

------------------------------------------------
-- Plans  (total_hours = 30 per plan)
-- GRADUATING_HOURS_THRESHOLD = 21
-- students with <= 21 remaining hours (passed >= 3 courses = 9h) are "graduating"
------------------------------------------------
INSERT INTO [plan] (plan_id, plan_name, major_id, total_hours) VALUES
(1, 'AI Plan', 1, 30),
(2, 'SE Plan', 2, 30),
(3, 'CY Plan', 3, 30);

------------------------------------------------
-- Courses: 30 total (10 per major)
-- Prereq chain creates demand at each academic level
------------------------------------------------

-- AI courses (IDs 101-110)
INSERT INTO course (course_id, course_na, credit_hours, type, major_id, plan_id, prereq_id) VALUES
(101, 'Intro to Programming',        3, 'Lecture', 1, 1, NULL),
(102, 'Data Structures',             3, 'Lecture', 1, 1, 101),
(103, 'Linear Algebra',              3, 'Lecture', 1, 1, NULL),
(104, 'Probability and Statistics',  3, 'Lecture', 1, 1, 103),
(105, 'Database Systems',            3, 'Lecture', 1, 1, 102),
(106, 'Machine Learning',            3, 'Lecture', 1, 1, 104),
(107, 'Computer Vision',             3, 'Lecture', 1, 1, 106),
(108, 'Natural Language Processing', 3, 'Lecture', 1, 1, 106),
(109, 'Deep Learning',               3, 'Lab',     1, 1, 106),
(110, 'AI Ethics',                   3, 'Lecture', 1, 1, NULL);

-- SE courses (IDs 201-210)
INSERT INTO course (course_id, course_na, credit_hours, type, major_id, plan_id, prereq_id) VALUES
(201, 'Intro to Programming',   3, 'Lecture', 2, 2, NULL),
(202, 'Data Structures',        3, 'Lecture', 2, 2, 201),
(203, 'Software Requirements',  3, 'Lecture', 2, 2, NULL),
(204, 'Database Systems',       3, 'Lecture', 2, 2, 202),
(205, 'Software Design',        3, 'Lecture', 2, 2, 203),
(206, 'Software Testing',       3, 'Lecture', 2, 2, 205),
(207, 'Web Development',        3, 'Lecture', 2, 2, 204),
(208, 'Mobile Development',     3, 'Lecture', 2, 2, 207),
(209, 'Software Architecture',  3, 'Lecture', 2, 2, 206),
(210, 'DevOps',                 3, 'Lecture', 2, 2, 209);

-- CY courses (IDs 301-310)
INSERT INTO course (course_id, course_na, credit_hours, type, major_id, plan_id, prereq_id) VALUES
(301, 'Intro to Programming',    3, 'Lecture', 3, 3, NULL),
(302, 'Data Structures',         3, 'Lecture', 3, 3, 301),
(303, 'Networking Fundamentals', 3, 'Lecture', 3, 3, NULL),
(304, 'Operating Systems',       3, 'Lecture', 3, 3, 302),
(305, 'Network Security',        3, 'Lecture', 3, 3, 303),
(306, 'Cryptography',            3, 'Lecture', 3, 3, 305),
(307, 'Ethical Hacking',         3, 'Lab',     3, 3, 305),
(308, 'Digital Forensics',       3, 'Lab',     3, 3, 307),
(309, 'Malware Analysis',        3, 'Lab',     3, 3, 307),
(310, 'Cyber Security Project',  3, 'Lecture', 3, 3, 306);

GO

------------------------------------------------
-- Instructors: 30 total (10 per major), all Doctor
-- Doctor load = 15 credit hours = 5 sections x 3 credits each
-- MAX_SECTIONS_PER_COURSE = 3 -> max 90 sections total needed
-- 30 instructors x 5 sections = 150 capacity > 90 needed
------------------------------------------------
DECLARE @iid INT = 1;
DECLARE @ispec NVARCHAR(10);

WHILE @iid <= 30
BEGIN
    SET @ispec = CASE
        WHEN @iid <= 10 THEN 'AI'
        WHEN @iid <= 20 THEN 'SE'
        ELSE 'CY'
    END;
    INSERT INTO instructor (instructor_id, instructor_name, spec, degree_type)
    VALUES (
        @iid,
        CONCAT('Dr_', @ispec, '_', FORMAT(@iid, '00')),
        @ispec,
        'Doctor'
    );
    SET @iid = @iid + 1;
END;

GO

------------------------------------------------
-- Rooms: 20 total
--   15 Lecture rooms (capacity 60 each)
--   5  Lab rooms     (capacity 30 each)
--
-- 10 time-pairs x 15 lecture rooms = 150 lecture slots > 90 needed
-- 10 time-pairs x 5  lab rooms     = 50  lab slots     > 12 lab sections needed
------------------------------------------------
DECLARE @rid INT = 1;

WHILE @rid <= 15
BEGIN
    INSERT INTO room (room_id, building, capacity, type)
    VALUES (@rid, CONCAT('IT Building - Hall ', FORMAT(@rid, '00')), 60, 'Lecture');
    SET @rid = @rid + 1;
END;

WHILE @rid <= 20
BEGIN
    INSERT INTO room (room_id, building, capacity, type)
    VALUES (@rid, CONCAT('IT Building - Lab ', FORMAT(@rid - 15, '00')), 30, 'Lab');
    SET @rid = @rid + 1;
END;

GO

------------------------------------------------
-- Time slots: 20 slots = 10 paired slots
-- Scheduler pairs Sun+Tue and Mon+Wed at the same clock time
-- ALLOWED_START = 08:00, ALLOWED_END = 16:00
------------------------------------------------
INSERT INTO time_slot (time_id, day, s_time, e_time) VALUES
-- Sunday + Tuesday pairs (5 pairs)
( 1, 'Sunday',    '08:00', '09:30'),
( 2, 'Tuesday',   '08:00', '09:30'),
( 3, 'Sunday',    '09:30', '11:00'),
( 4, 'Tuesday',   '09:30', '11:00'),
( 5, 'Sunday',    '11:00', '12:30'),
( 6, 'Tuesday',   '11:00', '12:30'),
( 7, 'Sunday',    '12:30', '14:00'),
( 8, 'Tuesday',   '12:30', '14:00'),
( 9, 'Sunday',    '14:00', '15:30'),
(10, 'Tuesday',   '14:00', '15:30'),
-- Monday + Wednesday pairs (5 pairs)
(11, 'Monday',    '08:00', '09:30'),
(12, 'Wednesday', '08:00', '09:30'),
(13, 'Monday',    '09:30', '11:00'),
(14, 'Wednesday', '09:30', '11:00'),
(15, 'Monday',    '11:00', '12:30'),
(16, 'Wednesday', '11:00', '12:30'),
(17, 'Monday',    '12:30', '14:00'),
(18, 'Wednesday', '12:30', '14:00'),
(19, 'Monday',    '14:00', '15:30'),
(20, 'Wednesday', '14:00', '15:30');

------------------------------------------------
-- Semester
------------------------------------------------
INSERT INTO semester (semester_id, name, s_date, e_date, status) VALUES
(1, 'Semester 1 - 2025/2026', '2025-09-01', '2026-01-15', 'active');

GO

------------------------------------------------
-- Students: 10,000 (IDs 10001-20000)
--
-- Major (std_id % 3):
--   1 -> AI (major_id=1)  ~3333 students
--   2 -> SE (major_id=2)  ~3334 students
--   0 -> CY (major_id=3)  ~3333 students
--
-- Level (std_id % 4):
--   1 -> Freshman  (0 courses passed)   ~2500
--   2 -> Sophomore (2 courses passed)   ~2500
--   3 -> Junior    (4 courses passed)   ~2500
--   0 -> Senior    (6-8 courses passed) ~2500
------------------------------------------------
DECLARE @i INT = 1;
DECLARE @major_id INT;

WHILE @i <= 10000
BEGIN
    SET @major_id = CASE
        WHEN @i % 3 = 1 THEN 1
        WHEN @i % 3 = 2 THEN 2
        ELSE 3
    END;

    INSERT INTO std (std_id, std_na, major_id)
    VALUES (10000 + @i, CONCAT('Student_', 10000 + @i), @major_id);

    SET @i = @i + 1;
END;

GO

------------------------------------------------
-- Student course history (~32,500 records)
--
-- Graduation check (GRADUATING_HOURS_THRESHOLD = 21):
--   Freshman  -> 0h done,  30h remaining -> NOT graduating
--   Sophomore -> 6h done,  24h remaining -> NOT graduating
--   Junior    -> 12h done, 18h remaining -> IS graduating (18 <= 21)
--   Senior    -> 18-24h done, 6-12h rem  -> IS graduating
--
-- AI level progression:
--   Soph   passed: 101, 103
--   Junior passed: 101, 102, 103, 104
--   Senior passed: 101, 102, 103, 104, 105, 106
--   Senior needs : 107 (Computer Vision), 108 (NLP), 109 (Deep Learning), 110 (AI Ethics)
--
-- SE level progression:
--   Soph   passed: 201, 203
--   Junior passed: 201, 202, 203, 205
--   Senior passed: 201, 202, 203, 204, 205, 206, 207, 209
--   Senior needs : 208 (Mobile Dev), 210 (DevOps)
--
-- CY level progression:
--   Soph   passed: 301, 303
--   Junior passed: 301, 302, 303, 305
--   Senior passed: 301, 302, 303, 304, 305, 306, 307
--   Senior needs : 308 (Digital Forensics), 309 (Malware Analysis), 310 (CY Project)
------------------------------------------------
DECLARE @hist_id INT = 1;
DECLARE @sid     INT = 10001;
DECLARE @lv      INT;
DECLARE @maj     INT;

WHILE @sid <= 20000
BEGIN
    SET @maj = CASE
        WHEN @sid % 3 = 1 THEN 1
        WHEN @sid % 3 = 2 THEN 2
        ELSE 3
    END;

    SET @lv = @sid % 4;
    IF @lv = 0 SET @lv = 4;

    -- SOPHOMORE: passed level-1 courses
    IF @lv >= 2
    BEGIN
        IF @maj = 1
        BEGIN
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 101, 1, 'B', 'passed', '1');
            SET @hist_id = @hist_id + 1;
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 103, 1, 'B', 'passed', '1');
            SET @hist_id = @hist_id + 1;
        END
        IF @maj = 2
        BEGIN
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 201, 1, 'B', 'passed', '1');
            SET @hist_id = @hist_id + 1;
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 203, 1, 'B', 'passed', '1');
            SET @hist_id = @hist_id + 1;
        END
        IF @maj = 3
        BEGIN
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 301, 1, 'B', 'passed', '1');
            SET @hist_id = @hist_id + 1;
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 303, 1, 'B', 'passed', '1');
            SET @hist_id = @hist_id + 1;
        END
    END

    -- JUNIOR: also passed level-2 courses
    IF @lv >= 3
    BEGIN
        IF @maj = 1
        BEGIN
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 102, 1, 'C', 'passed', '1');
            SET @hist_id = @hist_id + 1;
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 104, 1, 'C', 'passed', '1');
            SET @hist_id = @hist_id + 1;
        END
        IF @maj = 2
        BEGIN
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 202, 1, 'C', 'passed', '1');
            SET @hist_id = @hist_id + 1;
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 205, 1, 'C', 'passed', '1');
            SET @hist_id = @hist_id + 1;
        END
        IF @maj = 3
        BEGIN
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 302, 1, 'C', 'passed', '1');
            SET @hist_id = @hist_id + 1;
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 305, 1, 'C', 'passed', '1');
            SET @hist_id = @hist_id + 1;
        END
    END

    -- SENIOR: also passed level-3 courses (all seniors are graduating)
    IF @lv >= 4
    BEGIN
        IF @maj = 1  -- AI: 6 courses done, 12h remaining -> graduating, needs 107,108,109,110
        BEGIN
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 105, 1, 'B', 'passed', '1');
            SET @hist_id = @hist_id + 1;
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 106, 1, 'B', 'passed', '1');
            SET @hist_id = @hist_id + 1;
        END
        IF @maj = 2  -- SE: 8 courses done, 6h remaining -> graduating, needs 208, 210
        BEGIN
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 204, 1, 'B', 'passed', '1');
            SET @hist_id = @hist_id + 1;
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 206, 1, 'B', 'passed', '1');
            SET @hist_id = @hist_id + 1;
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 207, 1, 'B', 'passed', '1');
            SET @hist_id = @hist_id + 1;
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 209, 1, 'B', 'passed', '1');
            SET @hist_id = @hist_id + 1;
        END
        IF @maj = 3  -- CY: 7 courses done, 9h remaining -> graduating, needs 308,309,310
        BEGIN
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 304, 1, 'B', 'passed', '1');
            SET @hist_id = @hist_id + 1;
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 306, 1, 'B', 'passed', '1');
            SET @hist_id = @hist_id + 1;
            INSERT INTO std_course (history_id, std_id, course_id, semester_id, garde, status, section)
            VALUES (@hist_id, @sid, 307, 1, 'B', 'passed', '1');
            SET @hist_id = @hist_id + 1;
        END
    END

    SET @sid = @sid + 1;
END;

GO

------------------------------------------------
-- SUMMARY
-- Students   : 10,000  (IDs 10001-20000)
-- Courses    : 30      (10 per major, 4 levels via prereqs)
-- Instructors: 30      (10 per major, Doctor = 15h load)
-- Rooms      : 20      (15 Lecture x60 + 5 Lab x30)
-- Time slots : 20      (10 Sun/Tue pairs + 10 Mon/Wed pairs)
-- Std_course : ~32,500 records
--
-- Graduating students (~5,000 Juniors + Seniors) get priority scheduling
------------------------------------------------
