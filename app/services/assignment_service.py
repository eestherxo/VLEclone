from app.db import get_connection


def get_assignments_by_course(course_code, student_id=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    if student_id:
        query = """
            SELECT 
                ce.eventID AS assignmentID,
                ce.eventName AS assignmentName,
                ce.dueDate,
                ce.courseCode,
                s.filePath AS my_submission,
                (SELECT COUNT(*) FROM Submission WHERE assignmentID = ce.eventID) AS submission_count
            FROM CalendarEvent ce
            JOIN Assignment a ON ce.eventID = a.assignmentID
            LEFT JOIN Submission s ON s.assignmentID = ce.eventID AND s.studentID = %s
            WHERE ce.courseCode = %s
        """
        cursor.execute(query, (student_id, course_code))
    else:
        query = """
            SELECT 
                ce.eventID AS assignmentID,
                ce.eventName AS assignmentName,
                ce.dueDate,
                ce.courseCode,
                (SELECT COUNT(*) FROM Submission WHERE assignmentID = ce.eventID) AS submission_count
            FROM CalendarEvent ce
            JOIN Assignment a ON ce.eventID = a.assignmentID
            WHERE ce.courseCode = %s
        """
        cursor.execute(query, (course_code,))
    
    assignments = cursor.fetchall()
    cursor.close()
    conn.close()
    return assignments


def create_assignment(course_code, assignment_name, due_date):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # first create the calendar event
        cursor.execute(
            "INSERT INTO CalendarEvent (courseCode, eventName, createdDate, dueDate) VALUES (%s, %s, CURDATE(), %s)",
            (course_code, assignment_name, due_date)
        )
        event_id = cursor.lastrowid
        # then mark it as an assignment
        cursor.execute("INSERT INTO Assignment (assignmentID) VALUES (%s)", (event_id,))
        conn.commit()
        return event_id
    finally:
        cursor.close()
        conn.close()


def submit_assignment(student_id, assignment_id, file_path):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Submission (studentID, assignmentID, filePath) VALUES (%s, %s, %s)",
            (student_id, assignment_id, file_path)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def grade_assignment(lecturer_id, assignment_id, student_id, grade_value):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT filePath FROM Submission WHERE studentID = %s AND assignmentID = %s",
            (student_id, assignment_id)
        )
        if not cursor.fetchone():
            raise Exception("Student has not submitted this assignment")
        cursor.execute(
            """INSERT INTO Grade (lecID, assignmentID, studentID, gradeValue) 
               VALUES (%s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE gradeValue = %s""",
            (lecturer_id, assignment_id, student_id, grade_value, grade_value)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def get_submissions(assignment_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT 
            s.studentID AS student_id,
            CONCAT(u.firstName, ' ', u.lastName) AS username,
            s.filePath AS content,
            g.gradeValue AS grade
        FROM Submission s
        JOIN User u ON s.studentID = u.userID
        LEFT JOIN Grade g ON s.studentID = g.studentID AND s.assignmentID = g.assignmentID
        WHERE s.assignmentID = %s
    """
    cursor.execute(query, (assignment_id,))
    submissions = cursor.fetchall()
    cursor.close()
    conn.close()
    return submissions