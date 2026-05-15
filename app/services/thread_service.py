from app.db import get_connection

def get_all_threads(forum_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = "SELECT * FROM Thread WHERE forumID = %s"
    cursor.execute(query, (forum_id,))
    
    threads = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return threads

def get_thread(thread_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = "SELECT * FROM Thread WHERE threadID = %s"
    cursor.execute(query, (thread_id,))
    
    thread = cursor.fetchone()
    cursor.close()
    connection.close()
    
    return thread

def create_thread(forum_id, thread_title, content):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = "INSERT INTO Thread (forumID, threadTitle, content) VALUES (%s, %s, %s)"
    cursor.execute(query, (forum_id, thread_title, content))
    
    connection.commit()
    cursor.close()
    connection.close()

def delete_thread(thread_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = "DELETE FROM Thread WHERE threadID = %s"
    cursor.execute(query, (thread_id,))
    
    connection.commit()
    cursor.close()
    connection.close()