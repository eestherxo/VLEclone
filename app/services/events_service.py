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
    connection = get_connection()
    cursor = connection.cursor()
    try:
        # check if already submitted
        cursor.execute(
            "SELECT filePath FROM Submission WHERE studentID = %s AND assignmentID = %s",
            (student_id, assignment_id)
        )
        existing = cursor.fetchone()
        if existing:
            # update instead of insert
            cursor.execute(
                "UPDATE Submission SET filePath = %s WHERE studentID = %s AND assignmentID = %s",
                (file_path, student_id, assignment_id)
            )
        else:
            cursor.execute(
                "INSERT INTO Submission (studentID, assignmentID, filePath) VALUES (%s, %s, %s)",
                (student_id, assignment_id, file_path)
            )
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def grade_assignment(lecturer_id, assignment_id, student_id, grade_value):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        # Verify student submitted
        cursor.execute(
            "SELECT filePath FROM Submission WHERE studentID = %s AND assignmentID = %s",
            (student_id, assignment_id)
        )
        if not cursor.fetchone():
            raise Exception("Student has not submitted this assignment")

        # Insert or update grade
        cursor.execute(
            """INSERT INTO Grade (lecID, assignmentID, studentID, gradeValue) 
               VALUES (%s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE gradeValue = %s""",
            (lecturer_id, assignment_id, student_id, grade_value, grade_value)
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def lecturer_owns_event(lecturer_id, event_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 1 FROM CalendarEvent ce
            JOIN Teach t ON ce.courseCode = t.courseCode
            WHERE ce.eventID = %s AND t.lecID = %s
        """, (event_id, lecturer_id))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()
