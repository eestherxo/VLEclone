DROP DATABASE IF EXISTS vleclone;
CREATE DATABASE vleclone;
USE vleclone;

-- =================== USER SYSTEM ===================

CREATE TABLE User (
    userID INT PRIMARY KEY,
    password VARCHAR(255),
    firstName VARCHAR(80),
    lastName VARCHAR(80),
    role VARCHAR(50)
);

CREATE TABLE Admin (
    adminID INT PRIMARY KEY,
    FOREIGN KEY (adminID) REFERENCES User(userID)
);

CREATE TABLE Student (
    studentID INT PRIMARY KEY,
    FOREIGN KEY (studentID) REFERENCES User(userID)
);

CREATE TABLE Lecturer (
    lecturerID INT PRIMARY KEY,
    department VARCHAR(255),
    FOREIGN KEY (lecturerID) REFERENCES User(userID)
);

-- =================== COURSE SYSTEM ===================

CREATE TABLE Course (
    courseCode VARCHAR(25) PRIMARY KEY,
    courseName VARCHAR(255)
);

CREATE TABLE Creates (
    adminID INT,
    courseCode VARCHAR(25),
    PRIMARY KEY (adminID, courseCode),
    FOREIGN KEY (adminID) REFERENCES Admin(adminID),
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode)
);

CREATE TABLE Enroll (
    studentID INT,
    courseCode VARCHAR(25),
    PRIMARY KEY (studentID, courseCode),
    FOREIGN KEY (studentID) REFERENCES Student(studentID),
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode)
);

CREATE TABLE Teaches (
    lecturerID INT,
    courseCode VARCHAR(25) UNIQUE,
    PRIMARY KEY (lecturerID, courseCode),
    FOREIGN KEY (lecturerID) REFERENCES Lecturer(lecturerID),
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode)
);

-- =================== CONTENT SYSTEM ===================

CREATE TABLE Section (
    secID INT PRIMARY KEY AUTO_INCREMENT,
    courseCode VARCHAR(25),
    secName VARCHAR(255),
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode)
);

CREATE TABLE CourseContent (
    contentID INT PRIMARY KEY AUTO_INCREMENT,
    secID INT,
    contentName VARCHAR(255),
    type ENUM('link', 'file', 'slide'),
    content TEXT,
    FOREIGN KEY (secID) REFERENCES Section(secID)
);

-- =================== FORUM SYSTEM ===================

CREATE TABLE Forum (
    forumID INT PRIMARY KEY AUTO_INCREMENT,
    courseCode VARCHAR(25),
    forumName VARCHAR(255),
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode)
);

CREATE TABLE Thread (
    threadID INT PRIMARY KEY AUTO_INCREMENT,
    forumID INT,
    threadTitle VARCHAR(255),
    content TEXT,
    FOREIGN KEY (forumID) REFERENCES Forum(forumID)
);

CREATE TABLE Reply (
    parentThreadID INT,
    childThreadID INT,
    PRIMARY KEY (parentThreadID, childThreadID),
    FOREIGN KEY (parentThreadID) REFERENCES Thread(threadID),
    FOREIGN KEY (childThreadID) REFERENCES Thread(threadID)
);

-- =================== CALENDAR & ASSIGNMENT ===================

CREATE TABLE CalendarEvent (
    eventID INT PRIMARY KEY AUTO_INCREMENT,
    courseCode VARCHAR(25),
    eventName VARCHAR(255),
    createdDate DATE,
    dueDate DATE,
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode)
);

CREATE TABLE Assignment (
    assignmentID INT PRIMARY KEY,
    maxGrade INT DEFAULT 100,
    FOREIGN KEY (assignmentID) REFERENCES CalendarEvent(eventID)
);

CREATE TABLE Submission (
    studentID INT,
    assignmentID INT,
    filePath VARCHAR(255),
    PRIMARY KEY (studentID, assignmentID),
    FOREIGN KEY (studentID) REFERENCES Student(studentID),
    FOREIGN KEY (assignmentID) REFERENCES Assignment(assignmentID)
);

CREATE TABLE Grade (
    lecturerID INT,
    studentID INT,
    assignmentID INT,
    score INT,

    PRIMARY KEY (studentID, assignmentID),
    FOREIGN KEY (lecturerID) REFERENCES Lecturer(lecturerID),
    FOREIGN KEY (studentID) REFERENCES Student(studentID),
    FOREIGN KEY (assignmentID) REFERENCES Assignment(assignmentID)
);

-- =================== Report Views ==========================

-- 1. All courses that have 50 or more students
CREATE OR REPLACE VIEW vw_courses_high_enrollment AS
SELECT courseCode, COUNT(studentID) AS total_students
FROM Enroll
GROUP BY courseCode
HAVING COUNT(studentID) >= 50;

-- 2. All students that do 5 or more courses
CREATE OR REPLACE VIEW vw_students_heavy_load AS
SELECT studentID, COUNT(courseCode) AS total_courses
FROM Enroll
GROUP BY studentID
HAVING COUNT(courseCode) >= 5;

-- 3. All lecturers that teach 3 or more courses
CREATE OR REPLACE VIEW vw_lecturers_heavy_load AS
SELECT lecturerID, COUNT(courseCode) AS total_courses
FROM Teaches
GROUP BY lecturerID
HAVING COUNT(courseCode) >= 3;

-- 4. The 10 most enrolled courses
CREATE OR REPLACE VIEW vw_top_10_enrolled_courses AS
SELECT *
FROM (
    SELECT courseCode, COUNT(studentID) AS total_students
    FROM Enroll
    GROUP BY courseCode
    ORDER BY total_students DESC
    LIMIT 10
) AS top_courses;

-- 5. The top 10 students with the highest overall averages
CREATE OR REPLACE VIEW vw_top_10_students_averages AS
SELECT *
FROM (
    SELECT studentID, ROUND(AVG(grade), 2) AS overall_average
    FROM Grade
    GROUP BY studentID
    ORDER BY overall_average DESC
    LIMIT 10
) AS top_students;

/*
Check for Constraints:

SELECT studentID FROM Enroll GROUP BY studentID 
HAVING COUNT(courseCode) > 6;

SELECT studentID FROM Enroll GROUP BY studentID 
HAVING COUNT(courseCode) < 3;

SELECT courseCode FROM Enroll GROUP BY courseCode 
HAVING COUNT(studentID) < 10;

SELECT lecturerID FROM Teaches GROUP BY lecturerID 
HAVING COUNT(courseCode) > 5;

SELECT l.lecturerID FROM Lecturer l 
LEFT JOIN Teaches t ON l.lecturerID = t.lecturerID 
GROUP BY l.lecturerID HAVING COUNT(t.courseCode) = 0;
*/