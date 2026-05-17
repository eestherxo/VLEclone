from app.db import get_connection

def get_course_events(course_code):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT eventName, createdDate, dueDate, courseCode FROM CalendarEvent WHERE courseCode = %s"
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
        JOIN Enroll en ON e.courseCode = en.courseCode
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


def create_assignment(event_id):
    """Mark a calendar event as an assignment"""
    connection = get_connection()
    cursor = connection.cursor()

    query = "INSERT INTO Assignment (assignmentID) VALUES (%s)"
    cursor.execute(query, (event_id,))

    connection.commit()
    cursor.close()
    connection.close()


def submit_assignment(student_id, assignment_id, file_path):
    """Student submits an assignment"""
    connection = get_connection()
    cursor = connection.cursor()

    query = "INSERT INTO Submission (studentID, assignmentID, filePath) VALUES (%s, %s, %s)"
    cursor.execute(query, (student_id, assignment_id, file_path))

    connection.commit()
    cursor.close()
    connection.close()


def grade_assignment(lecturer_id, assignment_id, student_id, grade_value):
    """Lecturer grades a student's assignment"""
    connection = get_connection()
    cursor = connection.cursor()

    # Verify student submitted the assignment
    verify_query = "SELECT filePath FROM Submission WHERE studentID = %s AND assignmentID = %s"
    cursor.execute(verify_query, (student_id, assignment_id))
    if not cursor.fetchone():
        cursor.close()
        connection.close()
        raise Exception("Student has not submitted this assignment")

    # Insert grade record
    query = "INSERT INTO Grade (lecturerID, assignmentID) VALUES (%s, %s)"
    cursor.execute(query, (lecturer_id, assignment_id))

    # Update the grade value in Assignment table
    update_query = "UPDATE Assignment SET grade = %s WHERE assignmentID = %s"
    cursor.execute(update_query, (grade_value, assignment_id))

    connection.commit()
    cursor.close()
    connection.close()

def lecturer_owns_event(lecturer_id, event_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT *
        FROM CourseEvent ce
        JOIN Teaches t
            ON ce.courseCode = t.courseCode
        WHERE ce.eventID = %s
        AND t.lecturerID = %s
    """

    cursor.execute(query, (event_id, lecturer_id))

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result is not None