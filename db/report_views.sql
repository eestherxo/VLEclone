-- 1. All courses that have 50 or more students
CREATE VIEW vw_courses_high_enrollment AS
SELECT courseCode, COUNT(studentID) AS total_students
FROM Enroll
GROUP BY courseCode
HAVING COUNT(studentID) >= 50;

-- 2. All students that do 5 or more courses
CREATE VIEW vw_students_heavy_load AS
SELECT studentID, COUNT(courseCode) AS total_courses
FROM Enroll
GROUP BY studentID
HAVING COUNT(courseCode) >= 5;

-- 3. All lecturers that teach 3 or more courses
CREATE VIEW vw_lecturers_heavy_load AS
SELECT lecturerID, COUNT(courseCode) AS total_courses
FROM Teaches
GROUP BY lecturerID
HAVING COUNT(courseCode) >= 3;

-- 4. The 10 most enrolled courses
CREATE VIEW vw_top_10_enrolled_courses AS
SELECT courseCode, COUNT(studentID) AS total_students
FROM Enroll
GROUP BY courseCode
ORDER BY total_students DESC
LIMIT 10;

-- 5. The top 10 students with the highest overall averages
CREATE VIEW vw_top_10_students_averages AS
SELECT studentID, ROUND(AVG(grade), 2) AS overall_average
FROM Grade
GROUP BY studentID
ORDER BY overall_average DESC
LIMIT 10;