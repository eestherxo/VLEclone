from app.db import get_connection

def get_course_events(course_code):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT eventName FROM Event WHERE courseCode = %s"
    cursor.execute(query, (course_code,))
    events = cursor.fetchall()

    cursor.close()
    connection.close()
    return events


def get_student_events(student_id, event_date):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT e.eventName 
        FROM CalendarEvent AS e
        JOIN Enroll AS en ON e.courseCode = en.courseCode
        WHERE en.studentID = %s AND e.eventDate = %s
    """
    cursor.execute(query, (student_id, event_date))
    events = cursor.fetchall()

    cursor.close()
    connection.close()
    return events



def insert_event(course_code, event_name, event_date):
    connection = get_connection()
    cursor = connection.cursor()

    query = "INSERT INTO CalendarEvent (courseCode, eventName, eventDate) VALUES (%s, %s, %s)"
    cursor.execute(query, (course_code, event_name, event_date))

    connection.commit()
    cursor.close()
    connection.close()