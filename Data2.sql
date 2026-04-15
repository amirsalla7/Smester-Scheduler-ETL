-- =========================
-- ROOMS
-- =========================

INSERT INTO Rooms VALUES
('A101','A',1,80,'lecture'),('A102','A',1,80,'lecture'),
('A103','A',1,80,'lecture'),('A104','A',1,80,'lecture'),
('A105','A',1,80,'lecture'),('A106','A',1,80,'lecture'),
('A107','A',1,80,'lecture'),('A108','A',1,80,'lecture'),
('A109','A',1,80,'lecture'),('A110','A',1,80,'lecture'),

('A301','A',3,45,'lecture'),('A302','A',3,45,'lecture'),
('A303','A',3,45,'lecture'),('A304','A',3,45,'lecture'),
('A305','A',3,45,'lecture'),('A306','A',3,45,'lecture'),
('A307','A',3,45,'lecture'),('A308','A',3,45,'lecture'),
('A309','A',3,45,'lecture'),('A310','A',3,45,'lecture'),

('A401','A',4,25,'lab'),('A402','A',4,25,'lab'),
('A403','A',4,25,'lab'),('A404','A',4,25,'lab'),
('A405','A',4,25,'lab'),('A406','A',4,25,'lab'),
('A407','A',4,25,'lab'),('A408','A',4,25,'lab'),
('A409','A',4,25,'lab'),('A410','A',4,25,'lab'),

('C201','C',2,25,'lab'),
('C202','C',2,25,'lab');

-- =========================
-- COURSES
-- =========================

INSERT INTO Courses VALUES
('CY101','Programming 1','CY',1,'lecture'),
('CY102','Programming 2','CY',1,'lecture'),
('CY103','Discrete Mathematics','CY',1,'lecture'),
('CY104','Introduction to Cyber Security','CY',1,'lecture'),

('CY201','Data Structures','CY',2,'lecture'),
('CY202','Computer Organization','CY',2,'lecture'),
('CY203','Networking Fundamentals','CY',2,'lecture'),
('CY204','Operating Systems','CY',2,'lecture'),

('CY301','Network Security','CY',3,'lecture'),
('CY302','Cryptography','CY',3,'lecture'),
('CY303','Ethical Hacking','CY',3,'lab'),
('CY304','Secure Software Development','CY',3,'lecture'),

('CY401','Digital Forensics','CY',4,'lab'),
('CY402','Malware Analysis','CY',4,'lab'),
('CY403','Penetration Testing','CY',4,'lab'),
('CY404','Cyber Security Project','CY',4,'lecture'),

('SE101','Programming 1','SE',1,'lecture'),
('SE102','Programming 2','SE',1,'lecture'),
('SE201','Software Requirements','SE',2,'lecture'),
('SE202','Software Design','SE',2,'lecture'),
('SE203','Database Systems','SE',2,'lecture'),
('SE301','Software Testing','SE',3,'lecture'),
('SE302','Web Development','SE',3,'lecture'),
('SE303','Mobile App Development','SE',3,'lecture'),
('SE401','Software Architecture','SE',4,'lecture'),
('SE402','DevOps','SE',4,'lecture'),
('SE403','Software Project Management','SE',4,'lecture'),

('AI101','Programming 1','AI',1,'lecture'),
('AI102','Programming 2','AI',1,'lecture'),
('AI201','Linear Algebra','AI',2,'lecture'),
('AI202','Probability and Statistics','AI',2,'lecture'),
('AI203','Data Mining','AI',2,'lecture'),
('AI301','Machine Learning','AI',3,'lecture'),
('AI302','Computer Vision','AI',3,'lecture'),
('AI303','Natural Language Processing','AI',3,'lecture'),
('AI401','Deep Learning','AI',4,'lab'),
('AI402','Reinforcement Learning','AI',4,'lecture'),
('AI403','AI Ethics','AI',4,'lecture');

-- =========================
-- INSTRUCTORS
-- =========================

INSERT INTO Instructors VALUES
('D001','Dr_Ahmed_Salem','CY'),
('D002','Dr_Mohammad_Hassan','CY'),
('D003','Dr_Lina_Khaled','CY'),
('D004','Dr_Omar_Nasser','CY'),

('D005','Dr_Yousef_Ali','SE'),
('D006','Dr_Rana_Majed','SE'),
('D007','Dr_Khaled_Sami','SE'),
('D008','Dr_Nour_Hussein','SE'),

('D009','Dr_Sara_Adel','AI'),
('D010','Dr_Mahmoud_Zein','AI'),
('D011','Dr_Huda_Farouq','AI'),
('D012','Dr_Anas_Karim','AI');

-- =========================
-- STUDENTS (1000)
-- =========================

DECLARE @i INT = 1;

WHILE @i <= 1000
BEGIN
    DECLARE @major VARCHAR(5);
    DECLARE @year INT;
    DECLARE @gpa FLOAT;

    IF @i % 3 = 0 SET @major = 'CY';
    ELSE IF @i % 3 = 1 SET @major = 'SE';
    ELSE SET @major = 'AI';

    SET @year = (@i % 4) + 1;

    SET @gpa = ROUND((RAND(CHECKSUM(NEWID())) * 2) + 2, 2);

    INSERT INTO Students VALUES (
        'S' + RIGHT('0000' + CAST(@i AS VARCHAR),4),
        'Student_' + CAST(@i AS VARCHAR),
        @major,
        @year,
        @gpa
    );

    SET @i = @i + 1;
END
