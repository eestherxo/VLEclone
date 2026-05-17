from app.db import get_connection

def get_all_threads(forum_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT threadID, threadTitle, content FROM Thread WHERE forumID = %s", (forum_id,))
    threads = cursor.fetchall()
    cursor.close()
    connection.close()
    return threads

def get_thread(thread_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT threadID, threadTitle, content FROM Thread WHERE threadID = %s", (thread_id,))
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

def create_reply(parent_thread_id, content):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    # create new thread as the reply 
    child_query = """INSERT INTO Thread (forumID, threadTitle, content) VALUES (
        (SELECT forumID FROM Thread WHERE threadID = %s), 
        'Reply', %s
    )"""
    cursor.execute(child_query, (parent_thread_id, content))

    # new thread's ID will be the childThreadID in the Reply table
    child_thread_id = cursor.lastrowid

    # insert into Reply table create parent/child relationship
    reply_query = "INSERT INTO Reply (parentThreadID, childThreadID) VALUES (%s, %s)"
    cursor.execute(reply_query, (parent_thread_id, child_thread_id))

    connection.commit()
    cursor.close()
    connection.close()

    return child_thread_id

def get_replies(thread_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """SELECT t.threadID, t.threadTitle, t.content 
               FROM Thread t
               JOIN Reply r ON t.threadID = r.childThreadID
               WHERE r.parentThreadID = %s"""
    cursor.execute(query, (thread_id,))
    
    replies = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return replies