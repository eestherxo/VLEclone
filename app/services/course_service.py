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

    query = "SELECT courseName FROM Course"
    cursor.execute(query)
    courses = cursor.fetchall()

    cursor.close()
    connection.close()

    return [course["courseName"] for course in courses]


def get_student_courses(student_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT c.courseName
        FROM Course c
        JOIN Enrollment e ON c.courseCode = e.courseCode
        WHERE e.studentID = %s
    """
    cursor.execute(query, (student_id,))
    courses = cursor.fetchall()

    cursor.close()
    connection.close()

    return [course["courseName"] for course in courses]


def get_lecturer_courses(lecturer_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT c.courseName
        FROM Course c
        JOIN Teach t ON c.courseCode = t.courseCode
        WHERE t.lecturerID = %s
    """
    cursor.execute(query, (lecturer_id,))
    courses = cursor.fetchall()

    cursor.close()
    connection.close()

    return [course["courseName"] for course in courses]