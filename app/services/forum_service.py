from app.db import get_connection

def lecturer_teaches_course(lecturer_id, course_code):
    """Check if a lecturer teaches the given course"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Teach WHERE lecID = %s AND courseCode = %s", (lecturer_id, course_code))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result is not None

def get_all_forums(course_code):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT forumID, forumName FROM Forum WHERE courseCode = %s", (course_code,))
    forums = cursor.fetchall()
    cursor.close()
    connection.close()
    return forums

def get_forum(forum_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT forumID, forumName FROM Forum WHERE forumID = %s", (forum_id,))
    forum = cursor.fetchone()
    cursor.close()
    connection.close()
    return forum

def create_forum(course_code, forum_name):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = "INSERT INTO Forum (courseCode, forumName) VALUES (%s, %s)"
    cursor.execute(query, (course_code, forum_name))
    
    connection.commit()
    cursor.close()
    connection.close()

def delete_forum(forum_id):
    connection = get_connection()
    
    cursor = connection.cursor(dictionary=True)
    query = "DELETE FROM Forum WHERE forumID = %s"

    cursor.execute(query, (forum_id,))
    connection.commit()
    cursor.close()
    connection.close()