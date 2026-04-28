USE master;

------------------------------------------------
-- تنظيف البيانات القديمة
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
-- collage
------------------------------------------------
INSERT INTO collage (collage_id, collage_na) VALUES
(1, 'Faculty of Information Technology');

------------------------------------------------
-- department
------------------------------------------------
INSERT INTO department (department_id, department_na, collage_id) VALUES
(1, 'Artificial Intelligence', 1),
(2, 'Software Engineering', 1),
(3, 'Cyber Security', 1);

------------------------------------------------
-- major
------------------------------------------------
INSERT INTO major (major_id, major_na, credit_hours, department_id) VALUES
(1, 'AI', 30, 1),
(2, 'SE', 30, 2),
(3, 'CY', 30, 3);

------------------------------------------------
-- plan
------------------------------------------------
INSERT INTO [plan] (plan_id, plan_name, major_id, total_hours) VALUES
(1, 'AI Plan', 1, 30),
(2, 'SE Plan', 2, 30),
(3, 'CY Plan', 3, 30);

------------------------------------------------
-- instructor (6 doctors)
------------------------------------------------
INSERT INTO instructor (instructor_id, instructor_name, spec, degree_type) VALUES
(1, 'Dr Ahmad AI', 'AI', 'Doctor'),
(2, 'Dr Lina AI', 'AI', 'Doctor'),
(3, 'Dr Omar SE', 'SE', 'Doctor'),
(4, 'Dr Rana SE', 'SE', 'Doctor'),
(5, 'Dr Ali CY', 'CY', 'Doctor'),
(6, 'Dr Noor CY', 'CY', 'Doctor');

------------------------------------------------
-- room
------------------------------------------------
INSERT INTO room (room_id, building, capacity, type) VALUES
(1, 'IT Building', 30, 'Lecture'),
(2, 'IT Building', 40, 'Lecture'),
(3, 'IT Building', 35, 'Lecture'),
(4, 'IT Building', 25, 'Lab'),
(5, 'IT Building', 20, 'Lab');

------------------------------------------------
-- time_slot
------------------------------------------------
INSERT INTO time_slot (time_id, day, s_time, e_time) VALUES
(1, 'Sunday',    '08:00', '09:00'),
(2, 'Sunday',    '09:00', '10:00'),
(3, 'Sunday',    '10:00', '11:00'),
(4, 'Monday',    '08:00', '09:00'),
(5, 'Monday',    '09:00', '10:00'),
(6, 'Monday',    '10:00', '11:00'),
(7, 'Tuesday',   '08:00', '09:00'),
(8, 'Tuesday',   '09:00', '10:00'),
(9, 'Wednesday', '08:00', '09:00'),
(10,'Wednesday', '09:00', '10:00');

------------------------------------------------
-- semester
------------------------------------------------
INSERT INTO semester (semester_id, name, s_date, e_date, status) VALUES
(1, 'Winter 2025-2026', '2025-09-01', '2026-01-15', 'active');

------------------------------------------------
-- course (10 courses)
------------------------------------------------
INSERT INTO course (course_id, course_na, credit_hours, type, major_id, plan_id, prereq_id) VALUES
(1,  'Intro AI',            3, 'Lecture', 1, 1, NULL),
(2,  'Machine Learning',    3, 'Lecture', 1, 1, 1),
(3,  'Deep Learning',       3, 'Lecture', 1, 1, 2),
(4,  'AI Ethics',           3, 'Lecture', 1, 1, NULL),

(5,  'Software Design',     3, 'Lecture', 2, 2, NULL),
(6,  'Software Testing',    3, 'Lecture', 2, 2, 5),
(7,  'Requirements Eng',    3, 'Lecture', 2, 2, NULL),

(8,  'Cyber Intro',         3, 'Lecture', 3, 3, NULL),
(9,  'Network Security',    3, 'Lecture', 3, 3, 8),
(10, 'Ethical Hacking',     3, 'Lecture', 3, 3, 8);

------------------------------------------------
-- students (100 students)
------------------------------------------------
DECLARE @i INT = 1;

WHILE @i <= 100
BEGIN
    INSERT INTO std (std_id, std_na, major_id)
    VALUES (
        1000 + @i,
        CONCAT('Student ', @i),
        CASE 
            WHEN @i % 3 = 1 THEN 1
            WHEN @i % 3 = 2 THEN 2
            ELSE 3
        END
    );

    SET @i = @i + 1;
END;

------------------------------------------------
-- std_course
-- أول 10 طلاب خريجين (باقي لهم 18 ساعة أو أقل)
------------------------------------------------
INSERT INTO std_course (history_id, std_id, course_id, semester_id, grade, status, section) VALUES
(1, 1001, 1, 1, 'A', 'passed', '1'),
(2, 1001, 2, 1, 'B', 'passed', '1'),
(3, 1001, 3, 1, 'B', 'passed', '1'),
(4, 1001, 4, 1, 'A', 'passed', '1'),

(5, 1002, 5, 1, 'A', 'passed', '1'),
(6, 1002, 6, 1, 'B', 'passed', '1'),
(7, 1002, 7, 1, 'B', 'passed', '1'),
(8, 1002, 5, 1, 'A', 'passed', '1'),

(9, 1003, 8, 1, 'A', 'passed', '1'),
(10,1003, 9, 1, 'B', 'passed', '1'),
(11,1003,10, 1, 'B', 'passed', '1'),
(12,1003, 8, 1, 'A', 'passed', '1'),

(13,1004, 1, 1, 'A', 'passed', '1'),
(14,1004, 2, 1, 'B', 'passed', '1'),
(15,1004, 3, 1, 'B', 'passed', '1'),
(16,1004, 4, 1, 'A', 'passed', '1'),

(17,1005, 5, 1, 'A', 'passed', '1'),
(18,1005, 6, 1, 'B', 'passed', '1'),
(19,1005, 7, 1, 'B', 'passed', '1'),
(20,1005, 5, 1, 'A', 'passed', '1'),

(21,1006, 8, 1, 'A', 'passed', '1'),
(22,1006, 9, 1, 'B', 'passed', '1'),
(23,1006,10, 1, 'B', 'passed', '1'),
(24,1006, 8, 1, 'A', 'passed', '1'),

(25,1007, 1, 1, 'A', 'passed', '1'),
(26,1007, 2, 1, 'B', 'passed', '1'),
(27,1007, 3, 1, 'B', 'passed', '1'),
(28,1007, 4, 1, 'A', 'passed', '1'),

(29,1008, 5, 1, 'A', 'passed', '1'),
(30,1008, 6, 1, 'B', 'passed', '1'),
(31,1008, 7, 1, 'B', 'passed', '1'),
(32,1008, 5, 1, 'A', 'passed', '1'),

(33,1009, 8, 1, 'A', 'passed', '1'),
(34,1009, 9, 1, 'B', 'passed', '1'),
(35,1009,10, 1, 'B', 'passed', '1'),
(36,1009, 8, 1, 'A', 'passed', '1'),

(37,1010, 1, 1, 'A', 'passed', '1'),
(38,1010, 2, 1, 'B', 'passed', '1'),
(39,1010, 3, 1, 'B', 'passed', '1'),
(40,1010, 4, 1, 'A', 'passed', '1');

------------------------------------------------
-- باقي الطلاب: مواد أقل حتى يظلوا non-graduating
------------------------------------------------
DECLARE @history_id INT = 41;
DECLARE @student_id INT = 1011;

WHILE @student_id <= 1100
BEGIN
    IF (@student_id % 3 = 2)
    BEGIN
        INSERT INTO std_course (history_id, std_id, course_id, semester_id, grade, status, section)
        VALUES (@history_id, @student_id, 1, 1, 'B', 'passed', '1');
        SET @history_id = @history_id + 1;
    END
    ELSE IF (@student_id % 3 = 0)
    BEGIN
        INSERT INTO std_course (history_id, std_id, course_id, semester_id, grade, status, section)
        VALUES (@history_id, @student_id, 5, 1, 'B', 'passed', '1');
        SET @history_id = @history_id + 1;
    END
    ELSE
    BEGIN
        INSERT INTO std_course (history_id, std_id, course_id, semester_id, grade, status, section)
        VALUES (@history_id, @student_id, 8, 1, 'B', 'passed', '1');
        SET @history_id = @history_id + 1;
    END

    SET @student_id = @student_id + 1;
END;

