from app.db import get_connection


def insert_course(course_code, course_name):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = "INSERT INTO Course (courseCode, courseName) VALUES (%s, %s)"
    cursor.execute(query, (course_code, course_name))

    connection.commit()
    cursor.close()
    connection.close()


def get_courses():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT courseCode, courseName FROM Course"
    cursor.execute(query)
    courses = cursor.fetchall()
    cursor.close()
    connection.close()

    return courses


def get_student_courses(student_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT c.courseCode, c.courseName
        FROM Course c
        JOIN Enroll e ON c.courseCode = e.courseCode
        WHERE e.studentID = %s
    """
    cursor.execute(query, (student_id,))
    courses = cursor.fetchall()
    cursor.close()
    connection.close()

    return courses


def get_lecturer_courses(lecturer_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT c.courseCode, c.courseName
        FROM Course c
        JOIN Teaches t ON c.courseCode = t.courseCode
        WHERE t.lecturerID = %s
    """
    cursor.execute(query, (lecturer_id,))
    courses = cursor.fetchall()
    cursor.close()
    connection.close()

    return courses


def check_course_lecturer(course_code):
    """Checks if course has a lecturer assigned"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT lecturerID FROM Teaches WHERE courseCode = %s"
    cursor.execute(query, (course_code,))
    lecturer = cursor.fetchone()

    cursor.close()
    connection.close()

    return lecturer


def assign_lecturer(lecturer_id, course_code):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = "INSERT INTO Teaches (lecturerID, courseCode) VALUES (%s, %s)"
    cursor.execute(query, (lecturer_id, course_code))

    connection.commit()
    cursor.close()
    connection.close()


def insert_enrollment(student_id, course_code):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = "INSERT INTO Enroll (studentID, courseCode) VALUES (%s, %s)"
    cursor.execute(query, (student_id, course_code))

    connection.commit()
    cursor.close()
    connection.close()


def get_course_members(course_code):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT u.firstName, u.lastName, u.role
        FROM User u
        JOIN Enroll e ON u.userID = e.studentID
        WHERE e.courseCode = %s

        UNION 

        SELECT u.firstName, u.lastName, u.role
        FROM User u
        JOIN Teaches t ON u.userID = t.lecturerID
        WHERE t.courseCode = %s
    """
    cursor.execute(query, (course_code, course_code))
    members = cursor.fetchall()

    cursor.close()
    connection.close()

    return members

def lecturer_teaches_course(lecturer_id, course_code):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT *
        FROM Teaches
        WHERE lecturerID = %s
        AND courseCode = %s
    """

    cursor.execute(query, (lecturer_id, course_code))

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result is not None