DROP DATABASE IF EXISTS backup_project;
CREATE DATABASE backup_project;
USE backup_project;

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
    lecturerID INT PRIMARY KEY,
    department VARCHAR(255),
    FOREIGN KEY (lecturerID) REFERENCES User(userID)
);

CREATE TABLE Course (
    courseCode VARCHAR(255) PRIMARY KEY,
    courseName VARCHAR(255)
);

CREATE TABLE Enroll (
    studentID INT,
    courseCode VARCHAR(255),
    PRIMARY KEY (studentID, courseCode),
    FOREIGN KEY (studentID) REFERENCES Student(studentID),
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode)
);

CREATE TABLE Teaches (
    lecturerID INT,
    courseCode VARCHAR(255) UNIQUE,
    PRIMARY KEY (lecturerID, courseCode),
    FOREIGN KEY (lecturerID) REFERENCES Lecturer(lecturerID),
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode)
);

CREATE TABLE Creates (
    adminID INT,
    courseCode VARCHAR(255),
    PRIMARY KEY (adminID, courseCode),
    FOREIGN KEY (adminID) REFERENCES Admin(adminID),
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode)
);

CREATE TABLE Section (
    sectionID INT PRIMARY KEY AUTO_INCREMENT,
    courseCode VARCHAR(255),
    sectionName VARCHAR(255),
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode)
);

CREATE TABLE SectionItem(
    itemID INT PRIMARY KEY AUTO_INCREMENT,
    sectionID INT,
    itemName VARCHAR(255),
    itemType VARCHAR(255),
    content TEXT,
    FOREIGN KEY (sectionID) REFERENCES Section(sectionID)
);

CREATE TABLE Adds (
    lecturerID INT,
    itemID INT,
    PRIMARY KEY (lecturerID, itemID),
    FOREIGN KEY (lecturerID) REFERENCES Lecturer(lecturerID),
    FOREIGN KEY (itemID) REFERENCES SectionItem(itemID)
);

CREATE TABLE CalendarEvent (
    eventID INT PRIMARY KEY AUTO_INCREMENT,
    courseCode VARCHAR(255),
    eventName VARCHAR(255),
    eventDate DATE,
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode)
);

CREATE TABLE Assignment (
    assignmentID INT PRIMARY KEY,
    grade INT,
    FOREIGN KEY (assignmentID) REFERENCES CalendarEvent(eventID)
);

CREATE TABLE Submits (
    studentID INT,
    assignmentID INT,
    PRIMARY KEY (studentID, assignmentID),
    FOREIGN KEY (studentID) REFERENCES Student(studentID),
    FOREIGN KEY (assignmentID) REFERENCES Assignment(assignmentID)
);

CREATE TABLE Grades (
    lecturerID INT,
    assignmentID INT,
    PRIMARY KEY (lecturerID, assignmentID),
    FOREIGN KEY (lecturerID) REFERENCES Lecturer(lecturerID),
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

SELECT lecturerID FROM Teaches GROUP BY lecturerID 
HAVING COUNT(courseCode) > 5;

SELECT l.lecturerID FROM Lecturer l 
LEFT JOIN Teaches t ON t.lecturerID = t.lecturerID 
GROUP BY l.lecturerID HAVING COUNT(t.courseCode) = 0;
*/