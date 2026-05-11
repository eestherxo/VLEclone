from app.db import get_connection

def get_course_forum(course_code):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Forum WHERE courseCode = %s", (course_code,))
    forums = cursor.fetchall()
    cursor.close()
    connection.close()
    return forums

def insert_forum(course_code, forum_name):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO Forum (courseCode, forumName) VALUES (%s, %s)",
        (course_code, forum_name)
    )
    connection.commit()
    cursor.close()
    connection.close()

def get_forum_threads(forum_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    # Only get top-level threads (parentThreadID is NULL)
    cursor.execute("""
        SELECT t.threadID, t.forumID, t.parentThreadID,
               t.threadTitle AS title, t.threadContent AS content,
               u.userID, CONCAT(u.firstName, ' ', u.lastName) AS username
        FROM Thread t
        JOIN User u ON t.userID = u.userID
        WHERE t.forumID = %s AND t.parentThreadID IS NULL
        ORDER BY t.threadID DESC
    """, (forum_id,))
    threads = cursor.fetchall()
    cursor.close()
    connection.close()
    return threads

def get_thread_replies(thread_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.threadID, t.parentThreadID,
               t.threadTitle AS title, t.threadContent AS content,
               u.userID, CONCAT(u.firstName, ' ', u.lastName) AS username
        FROM Thread t
        JOIN User u ON t.userID = u.userID
        WHERE t.parentThreadID = %s
        ORDER BY t.threadID ASC
    """, (thread_id,))
    replies = cursor.fetchall()
    cursor.close()
    connection.close()
    return replies

def insert_thread(forum_id, thread_title, thread_content, user_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """INSERT INTO Thread (forumID, userID, threadTitle, threadContent)
           VALUES (%s, %s, %s, %s)""",
        (forum_id, user_id, thread_title, thread_content)
    )
    connection.commit()
    cursor.close()
    connection.close()

def insert_reply(thread_id, user_id, content):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    # Get the parent thread's forumID so we can insert into same forum
    cursor.execute("SELECT forumID FROM Thread WHERE threadID = %s", (thread_id,))
    parent = cursor.fetchone()
    if not parent:
        cursor.close()
        connection.close()
        return

    cursor2 = connection.cursor()
    cursor2.execute(
        """INSERT INTO Thread (forumID, userID, parentThreadID, threadTitle, threadContent)
           VALUES (%s, %s, %s, %s, %s)""",
        (parent['forumID'], user_id, thread_id, 'Reply', content)
    )
    connection.commit()
    cursor2.close()
    cursor.close()
    connection.close()