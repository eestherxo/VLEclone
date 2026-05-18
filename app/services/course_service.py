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
        JOIN Teach t ON c.courseCode = t.courseCode
        WHERE t.lecID = %s
    """
    cursor.execute(query, (lecturer_id,))
    courses = cursor.fetchall()
    cursor.close()
    connection.close()
    return courses

def check_course_lecturer(course_code):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT lecID FROM Teach WHERE courseCode = %s", (course_code,))
    lecturer = cursor.fetchone()
    cursor.close()
    connection.close()
    return lecturer


def assign_lecturer(lecturer_id, course_code):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("INSERT INTO Teach (lecID, courseCode) VALUES (%s, %s)", (lecturer_id, course_code))
    connection.commit()
    cursor.close()
    connection.close()

def insert_enrollment(student_id, course_code):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("INSERT INTO Enroll (studentID, courseCode) VALUES (%s, %s)", (student_id, course_code))
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
        JOIN Teach t ON u.userID = t.lecID
        WHERE t.courseCode = %s
    """
    cursor.execute(query, (course_code, course_code))
    members = cursor.fetchall()
    cursor.close()
    connection.close()
    return members

def lecturer_teaches_course(user_id, course_code):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT 1 FROM Teach WHERE lecID = %s AND courseCode = %s",  # Teach not Teaches, lecID not userID
            (user_id, course_code),
        )
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()
