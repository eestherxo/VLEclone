from app.db import get_connection
from datetime import datetime


def create_assignment(course_code, assignment_name, due_date, lecturer_id):
    """Create an assignment for a course"""
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        # Insert into CalendarEvent first
        query_event = """
            INSERT INTO CalendarEvent (courseCode, eventName, eventDate) 
            VALUES (%s, %s, %s)
        """
        cursor.execute(query_event, (course_code, assignment_name, due_date))
        connection.commit()
        event_id = cursor.lastrowid
        
        # Insert into Assignment table
        query_assignment = "INSERT INTO Assignment (assignmentID) VALUES (%s)"
        cursor.execute(query_assignment, (event_id,))
        connection.commit()
        
        cursor.close()
        connection.close()
        return event_id
    except Exception as e:
        connection.close()
        raise e


def get_course_assignments(course_code):
    """Get all assignments for a course"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        query = """
            SELECT 
                a.assignmentID,
                ce.eventName as assignmentName,
                ce.eventDate as dueDate,
                a.grade
            FROM Assignment a
            JOIN CalendarEvent ce ON a.assignmentID = ce.eventID
            WHERE ce.courseCode = %s
            ORDER BY ce.eventDate
        """
        cursor.execute(query, (course_code,))
        assignments = cursor.fetchall()
        cursor.close()
        connection.close()
        return assignments
    except Exception as e:
        connection.close()
        raise e


def submit_assignment(student_id, assignment_id):
    """Student submits an assignment"""
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        # Check if already submitted
        check_query = "SELECT * FROM Submits WHERE studentID = %s AND assignmentID = %s"
        cursor.execute(check_query, (student_id, assignment_id))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return {"error": "Student has already submitted this assignment"}
        
        # Record submission
        query = "INSERT INTO Submits (studentID, assignmentID) VALUES (%s, %s)"
        cursor.execute(query, (student_id, assignment_id))
        connection.commit()
        cursor.close()
        connection.close()
        return {"success": True}
    except Exception as e:
        connection.close()
        raise e


def grade_assignment(assignment_id, student_id, grade, lecturer_id):
    """Assign a grade to a student for an assignment"""
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        # Update the grade in Assignment table (noting this is for a specific submission)
        # Note: The schema has grade in Assignment table - we'll store average per assignment
        # In a production system, you might want a separate StudentGrade table
        query = """
            UPDATE Assignment 
            SET grade = %s 
            WHERE assignmentID = %s
        """
        cursor.execute(query, (grade, assignment_id))
        connection.commit()
        
        # Optionally record the grader
        # This would require extending the Grades table schema
        
        cursor.close()
        connection.close()
        return {"success": True}
    except Exception as e:
        connection.close()
        raise e


def get_student_grades(student_id):
    """Get all grades for a student"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        query = """
            SELECT 
                a.assignmentID,
                ce.eventName as assignmentName,
                ce.courseCode,
                a.grade,
                ce.eventDate as dueDate
            FROM Submits s
            JOIN Assignment a ON s.assignmentID = a.assignmentID
            JOIN CalendarEvent ce ON a.assignmentID = ce.eventID
            WHERE s.studentID = %s
            ORDER BY ce.eventDate DESC
        """
        cursor.execute(query, (student_id,))
        grades = cursor.fetchall()
        cursor.close()
        connection.close()
        return grades
    except Exception as e:
        connection.close()
        raise e


def get_student_final_average(student_id, course_code=None):
    """Calculate final average for a student (across all courses or specific course)"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        if course_code:
            query = """
                SELECT 
                    ce.courseCode,
                    AVG(a.grade) as average,
                    COUNT(a.grade) as assignment_count
                FROM Submits s
                JOIN Assignment a ON s.assignmentID = a.assignmentID
                JOIN CalendarEvent ce ON a.assignmentID = ce.eventID
                WHERE s.studentID = %s AND ce.courseCode = %s AND a.grade IS NOT NULL
                GROUP BY ce.courseCode
            """
            cursor.execute(query, (student_id, course_code))
        else:
            query = """
                SELECT 
                    ce.courseCode,
                    AVG(a.grade) as average,
                    COUNT(a.grade) as assignment_count
                FROM Submits s
                JOIN Assignment a ON s.assignmentID = a.assignmentID
                JOIN CalendarEvent ce ON a.assignmentID = ce.eventID
                WHERE s.studentID = %s AND a.grade IS NOT NULL
                GROUP BY ce.courseCode
            """
            cursor.execute(query, (student_id,))
        
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        
        # Calculate overall average
        if results:
            overall_avg = sum(r['average'] for r in results) / len(results)
        else:
            overall_avg = None
        
        return {
            "courses": results,
            "overall_average": overall_avg
        }
    except Exception as e:
        connection.close()
        raise e


def get_assignment_submissions(assignment_id):
    """Get all submissions for an assignment (lecturer view)"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        query = """
            SELECT 
                s.studentID,
                u.firstName,
                u.lastName,
                a.assignmentID,
                a.grade
            FROM Submits s
            JOIN Student st ON s.studentID = st.studentID
            JOIN User u ON st.studentID = u.userID
            JOIN Assignment a ON s.assignmentID = a.assignmentID
            WHERE s.assignmentID = %s
            ORDER BY u.lastName, u.firstName
        """
        cursor.execute(query, (assignment_id,))
        submissions = cursor.fetchall()
        cursor.close()
        connection.close()
        return submissions
    except Exception as e:
        connection.close()
        raise e


def check_student_submission(student_id, assignment_id):
    """Check if a student has submitted an assignment"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        query = "SELECT * FROM Submits WHERE studentID = %s AND assignmentID = %s"
        cursor.execute(query, (student_id, assignment_id))
        submission = cursor.fetchone()
        cursor.close()
        connection.close()
        return submission is not None
    except Exception as e:
        connection.close()
        raise e
