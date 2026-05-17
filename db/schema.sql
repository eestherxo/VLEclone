DROP DATABASE IF EXISTS vleclone;
CREATE DATABASE vleclone;
USE vleclone;

CREATE TABLE User (
    userID INT PRIMARY KEY,
    password VARCHAR(255),
    firstName VARCHAR(255),
    lastName VARCHAR(255),
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

CREATE TABLE Forum (
    forumID INT PRIMARY KEY AUTO_INCREMENT,
    courseCode VARCHAR(255),
    forumName VARCHAR(255),
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode)
);

CREATE TABLE Thread (
    threadID INT PRIMARY KEY AUTO_INCREMENT,
    forumID INT,
    parentThreadID INT,
    threadTitle VARCHAR(255),
    threadContent TEXT,
    FOREIGN KEY (forumID) REFERENCES Forum(forumID),
    FOREIGN KEY (parentThreadID) REFERENCES Thread(threadID)
);

CREATE TABLE Reply (
    userID INT,
    threadID INT,
    PRIMARY KEY (userID, threadID),
    FOREIGN KEY (userID) REFERENCES User(userID),
    FOREIGN KEY (threadID) REFERENCES Thread(threadID)
);

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