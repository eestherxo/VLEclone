from app.db import get_connection

def get_course_events(course_code):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT eventName, createdDate, dueDate FROM CalendarEvent WHERE course_code = %s"
    cursor.execute(query, (course_code,))
    events = cursor.fetchall()

    cursor.close()
    connection.close()
    
    return events


def get_student_events_by_date(student_id, due_date):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """
        SELECT e.eventName, e.createdDate, e.dueDate
        FROM CalendarEvent e
        JOIN Enroll en ON e.course_code = en.courseCode
        WHERE en.studentID = %s AND e.dueDate = %s
    """
    cursor.execute(query, (student_id, due_date))
    events = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return events


def insert_course_event(course_code, event_name, created_date, due_date):
    connection = get_connection()
    cursor = connection.cursor()

    query = "INSERT INTO CalendarEvent (courseCode, eventName, createdDate, dueDate) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (course_code, event_name, created_date, due_date))

    connection.commit()
    cursor.close()
    connection.close()

