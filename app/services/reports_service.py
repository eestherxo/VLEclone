from app.db import get_connection

def get_popular_courses():
    """Courses with 50 or more enrolled students"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM vw_courses_high_enrollment ORDER BY total_students DESC"
    cursor.execute(query)
    courses = cursor.fetchall()

    cursor.close()
    connection.close()

    return courses


def get_busy_students():
    """Students enrolled in 5 or more courses"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM vw_students_heavy_load ORDER BY total_courses DESC"
    cursor.execute(query)
    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return students


def get_busy_lecturers():
    """Lecturers teaching 3 or more courses"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM vw_lecturers_heavy_load ORDER BY total_courses DESC"
    cursor.execute(query)
    lecturers = cursor.fetchall()

    cursor.close()
    connection.close()

    return lecturers


def get_most_enrolled_courses():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM vw_top_10_enrolled_courses ORDER BY total_students DESC"
    cursor.execute(query)
    courses = cursor.fetchall()
    cursor.close()
    connection.close()
    return courses


def get_top_students():
    """The top 10 students by overall average grade"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM vw_top_10_students_averages ORDER BY overall_average DESC"
    cursor.execute(query)
    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return students