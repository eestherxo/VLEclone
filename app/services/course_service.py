from app.db import get_connection



def insert_course(course_code, course_name):
    connection = get_connection()
    cursor = connection.cursor()

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
        SELECT c.courseCode FROM Course AS c
        JOIN Enroll AS e ON c.courseCode = e.courseCode
        WHERE e.studentId = %s
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
        SELECT c.courseCode FROM Course AS c
        JOIN Teaches AS t ON c.courseCode = t.courseCode
        WHERE t.lecturerId = %s
    """
    cursor.execute(query, (lecturer_id,))
    courses = cursor.fetchall()

    cursor.close()
    connection.close()
    return courses

def insert_teaches(lecturer_id, course_code):
    connection = get_connection()
    cursor = connection.cursor()

    query = "INSERT INTO Teaches (lecturerId, courseCode) VALUES (%s, %s)"
    cursor.execute(query, (lecturer_id, course_code))

    connection.commit()
    cursor.close()
    connection.close()

def insert_enroll(student_id, course_code):
    connection = get_connection()
    cursor = connection.cursor()

    query = "INSERT INTO Enroll (studentID, courseCode) VALUES (%s, %s)"
    cursor.execute(query, (student_id, course_code))

    connection.commit()
    cursor.close()
    connection.close()

def get_course_members(course_code):
    connection = get_connection()
    cursor  = connection.cursor()

    query = """
        SELECT firstName, lastName FROM Student AS s
        JOIN Enroll AS e ON s.studentId = e.studentId
        WHERE e.courseCode = %s
        UNION
        SELECT firstName, lastName FROM Lecturer AS l
        JOIN Teaches AS t ON l.lecturerId = t.lecturerId
        WHERE t.courseCode = %s
    """
    cursor.execute(query, (course_code,))
    members = cursor.fetchall()

    cursor.close()
    connection.close()
    return members