from app.db import get_connection


def get_course_forum(course_code):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = "SELECT * FROM Forum WHERE course_code = %s"
    cursor.execute(query, (course_code,))
    forums = cursor.fetchone()

    cursor.close()
    connection.close()
    return forums    

def insert_forum(course_code, forum_name):
    connection = get_connection()
    cursor = connection.cursor()

    query = "INSERT INTO Forum (course_code, forum_name) VALUES (%s, %s)"
    cursor.execute(query, (course_code, forum_name))

    connection.commit()
    cursor.close()
    connection.close()


def get_forum_threads(forum_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM Thread WHERE forum_id = %s"
    cursor.execute(query, (forum_id,))
    threads = cursor.fetchall()

    cursor.close()
    connection.close()
    return threads

def insert_thread(forum_id, thread_title, thread_content):
    connection = get_connection()
    cursor = connection.cursor()

    query = "INSERT INTO Thread (forum_id, thread_title, thread_content) VALUES (%s, %s, %s)"
    cursor.execute(query, (forum_id, thread_title, thread_content))

    connection.commit()
    cursor.close()
    connection.close()
