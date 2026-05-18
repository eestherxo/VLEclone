from app.db import get_connection

def get_popular_courses():
    """Courses with 50 or more enrolled students"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM PopularCourses ORDER BY studentCount DESC"
    cursor.execute(query)
    courses = cursor.fetchall()

    cursor.close()
    connection.close()

    return courses


def get_busy_students():
    """Students enrolled in 5 or more courses"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM BusyStudents ORDER BY courseCount DESC"
    cursor.execute(query)
    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return students


def get_busy_lecturers():
    """Lecturers teaching 3 or more courses"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM BusyLecturers ORDER BY courseCount DESC"
    cursor.execute(query)
    lecturers = cursor.fetchall()

    cursor.close()
    connection.close()

    return lecturers


def get_most_enrolled_courses():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM TopEnrolledCourses ORDER BY studentCount DESC")  # was MostEnrolledCourses
    courses = cursor.fetchall()
    cursor.close()
    connection.close()
    return courses


def get_top_students():
    """The top 10 students by overall average grade"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM TopStudents ORDER BY averageGrade DESC"
    cursor.execute(query)
    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return students