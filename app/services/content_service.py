from app.db import get_connection


def insert_section(course_code, sec_name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Section (courseCode, secName) VALUES (%s, %s)",
            (course_code, sec_name),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def get_section(sec_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Section WHERE secID = %s", (sec_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_sections_by_course(course_code):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM Section WHERE courseCode = %s ORDER BY secID",
            (course_code,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def insert_course_content(sec_id, content_name, content_type, content):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO CourseContent (secID, contentName, type, content)
            VALUES (%s, %s, %s, %s)
            """,
            (sec_id, content_name, content_type, content),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def get_course_content_by_course(course_code):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                s.secID         AS secID,
                s.secName       AS secName,
                cc.contentID    AS contentID,
                cc.contentName  AS contentName,
                cc.type         AS type,
                cc.content      AS content
            FROM Section s
            LEFT JOIN CourseContent cc ON cc.secID = s.secID
            WHERE s.courseCode = %s
            ORDER BY s.secID, cc.contentID
            """,
            (course_code,),
        )
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    sections = {}
    for row in rows:
        sec_id = row["secID"]
        if sec_id not in sections:
            sections[sec_id] = {
                "secID": sec_id,
                "secName": row["secName"],
                "contentItems": [],
            }
        if row["contentID"] is not None:
            sections[sec_id]["contentItems"].append({
                "contentID": row["contentID"],
                "contentName": row["contentName"],
                "type": row["type"],
                "content": row["content"],
            })
    return list(sections.values())


def lecturer_teaches_course(user_id, course_code):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT 1 FROM Teach WHERE lecID = %s AND courseCode = %s",  # was userID
            (user_id, course_code),
        )
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()


def get_course_code_for_section(sec_id):
    """Look up the parent course of a section."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT courseCode FROM Section WHERE secID = %s", (sec_id,))
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        cursor.close()
        conn.close()