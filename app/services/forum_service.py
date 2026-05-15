from app.db import get_connection

def get_all_forums():
    connection = get_connection()
    
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM Forum"
    cursor.execute(query)
    
    forums = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return forums

def get_forum(forum_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = "SELECT * FROM Forum WHERE forumID = %s"
    cursor.execute(query, (forum_id,))
    
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