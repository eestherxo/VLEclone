from app.db import get_connection


def get_popular_courses():
    """All courses with 50 or more students"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            c.courseCode,
            c.courseName,
            COUNT(e.studentID) AS studentCount
        FROM Course c
        JOIN Enroll e ON c.courseCode = e.courseCode
        GROUP BY c.courseCode, c.courseName
        HAVING COUNT(e.studentID) >= 50
        ORDER BY studentCount DESC
    """)
    courses = cursor.fetchall()
    cursor.close()
    connection.close()
    return courses


def get_busy_students():
    """All students enrolled in 5 or more courses"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            u.userID AS student_id,
            CONCAT(u.firstName, ' ', u.lastName) AS username,
            COUNT(e.courseCode) AS courseCount
        FROM User u
        JOIN Student s ON s.studentID = u.userID
        JOIN Enroll e ON e.studentID = u.userID
        GROUP BY u.userID, u.firstName, u.lastName
        HAVING COUNT(e.courseCode) >= 5
        ORDER BY courseCount DESC
    """)
    students = cursor.fetchall()
    cursor.close()
    connection.close()
    return students


def get_busy_lecturers():
    """All lecturers teaching 3 or more courses"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            u.userID AS lecturer_id,
            CONCAT(u.firstName, ' ', u.lastName) AS username,
            COUNT(t.courseCode) AS courseCount
        FROM User u
        JOIN Lecturer l ON l.lecID = u.userID
        JOIN Teach t ON t.lecID = u.userID
        GROUP BY u.userID, u.firstName, u.lastName
        HAVING COUNT(t.courseCode) >= 3
        ORDER BY courseCount DESC
    """)
    lecturers = cursor.fetchall()
    cursor.close()
    connection.close()
    return lecturers


def get_most_enrolled_courses():
    """Top 10 most enrolled courses"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            c.courseCode,
            c.courseName,
            COUNT(e.studentID) AS studentCount
        FROM Course c
        JOIN Enroll e ON c.courseCode = e.courseCode
        GROUP BY c.courseCode, c.courseName
        ORDER BY studentCount DESC
        LIMIT 10
    """)
    courses = cursor.fetchall()
    cursor.close()
    connection.close()
    return courses


def get_top_students():
    """Top 10 students with highest overall average grade"""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                u.userID AS student_id,
                CONCAT(u.firstName, ' ', u.lastName) AS username,
                ROUND(AVG(sub.score), 2) AS averageGrade
            FROM User u
            JOIN Student s ON s.studentID = u.userID
            JOIN Submission sub ON sub.studentID = u.userID
            WHERE sub.score > 0
            GROUP BY u.userID, u.firstName, u.lastName
            ORDER BY averageGrade DESC
            LIMIT 10
        """)
        students = cursor.fetchall()
        cursor.close()
        connection.close()
        return students if students else []
    except Exception as e:
        return []