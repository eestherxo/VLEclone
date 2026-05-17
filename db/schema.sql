DROP DATABASE IF EXISTS vleclone;
CREATE DATABASE vleclone;
USE vleclone;

CREATE TABLE User (
    userID INT PRIMARY KEY,
    firstName VARCHAR(255),
    lastName VARCHAR(255),
    password VARCHAR(255),
    role VARCHAR(255)
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
    lecID INT PRIMARY KEY,
    department VARCHAR(255),
    FOREIGN KEY (lecID) REFERENCES User(userID)
);

CREATE TABLE Course (
    courseCode VARCHAR(255) PRIMARY KEY,
    courseName VARCHAR(255)
);

CREATE TABLE Creator (
    adminID INT,
    courseCode VARCHAR(255),
    PRIMARY KEY (adminID, courseCode),
    FOREIGN KEY (adminID) REFERENCES Admin(adminID),
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode)
);

CREATE TABLE Enroll (
    studentID INT,
    courseCode VARCHAR(255),
    PRIMARY KEY (studentID, courseCode),
    FOREIGN KEY (studentID) REFERENCES Student(studentID),
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode)
);

CREATE TABLE Teach (
    lecID INT,
    courseCode VARCHAR(255) UNIQUE,
    PRIMARY KEY (lecID, courseCode),
    FOREIGN KEY (lecID) REFERENCES Lecturer(lecID),
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode)
);


CREATE TABLE Section (
    secID INT PRIMARY KEY AUTO_INCREMENT,
    courseCode VARCHAR(255),
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

CREATE TABLE Forum (
    forumID INT PRIMARY KEY AUTO_INCREMENT,
    courseCode VARCHAR(255),
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


CREATE TABLE CalendarEvent (
    eventID INT PRIMARY KEY AUTO_INCREMENT,
    courseCode VARCHAR(255),
    eventName VARCHAR(255),
    createdDate DATE,
    dueDate DATE,
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode)
);

CREATE TABLE Assignment (
    assignmentID INT PRIMARY KEY,
    grade INT,
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
    lecID INT,
    assignmentID INT,
    PRIMARY KEY (lecID, assignmentID),
    FOREIGN KEY (lecID) REFERENCES Lecturer(lecID),
    FOREIGN KEY (assignmentID) REFERENCES Assignment(assignmentID)
);

/* Generating Reports */

CREATE OR REPLACE VIEW PopularCourses AS
SELECT
    c.courseCode,
    c.courseName,
    COUNT(e.userID) AS studentCount
FROM Course c
JOIN Enroll e ON e.courseCode = c.courseCode
GROUP BY c.courseCode, c.courseName
HAVING COUNT(e.userID) >= 50;


CREATE OR REPLACE VIEW BusyStudents AS
SELECT
    u.userID,
    u.firstName,
    u.lastName,
    COUNT(e.courseCode) AS courseCount
FROM User u
JOIN Student s ON s.userID = u.userID
JOIN Enroll e ON e.userID = u.userID
GROUP BY u.userID, u.firstName, u.lastName
HAVING COUNT(e.courseCode) >= 5;


CREATE OR REPLACE VIEW BusyLecturers AS
SELECT
    u.userID,
    u.firstName,
    u.lastName,
    l.department,
    COUNT(t.courseCode) AS courseCount
FROM User u
JOIN Lecturer l ON l.userID = u.userID
JOIN Teach t ON t.userID = u.userID
GROUP BY u.userID, u.firstName, u.lastName, l.department
HAVING COUNT(t.courseCode) >= 3;


CREATE OR REPLACE VIEW MostEnrolledCourses AS
SELECT
    c.courseCode,
    c.courseName,
    COUNT(e.userID) AS studentCount
FROM Course c
JOIN Enroll e ON e.courseCode = c.courseCode
GROUP BY c.courseCode, c.courseName
ORDER BY studentCount DESC
LIMIT 10;


CREATE OR REPLACE VIEW TopStudents AS
SELECT
    u.userID,
    u.firstName,
    u.lastName,
    AVG(g.score) AS averageGrade,
    COUNT(g.eventID) AS gradedCount
FROM User u
JOIN Student s ON s.userID = u.userID
JOIN Grade g ON g.userID = u.userID
GROUP BY u.userID, u.firstName, u.lastName
ORDER BY averageGrade DESC
LIMIT 10;

/* -------------------------------------------------------------------- */

/*
Check for Constraints:

SELECT studentID FROM Enroll GROUP BY studentID 
HAVING COUNT(courseCode) > 6;

SELECT studentID FROM Enroll GROUP BY studentID 
HAVING COUNT(courseCode) < 3;

SELECT courseCode FROM Enroll GROUP BY courseCode 
HAVING COUNT(studentID) < 10;

SELECT lecID FROM Teach GROUP BY lecID 
HAVING COUNT(courseCode) > 5;

SELECT l.lecID FROM Lecturer l 
LEFT JOIN Teach t ON t.lecID = t.lecID 
GROUP BY l.lecID HAVING COUNT(t.courseCode) = 0;
*/