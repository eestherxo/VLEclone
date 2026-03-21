from app.db import get_connection


def create_section(course_code, section_name):
    """Create a new section for a course"""
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        query = "INSERT INTO Section (courseCode, sectionName) VALUES (%s, %s)"
        cursor.execute(query, (course_code, section_name))
        connection.commit()
        section_id = cursor.lastrowid
        cursor.close()
        connection.close()
        return section_id
    except Exception as e:
        connection.close()
        raise e


def add_section_item(section_id, item_name, item_type, content):
    """Add content item to a section (type: link, file, or slides)"""
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        query = "INSERT INTO SectionItem (sectionID, itemName, itemType, content) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (section_id, item_name, item_type, content))
        connection.commit()
        item_id = cursor.lastrowid
        cursor.close()
        connection.close()
        return item_id
    except Exception as e:
        connection.close()
        raise e


def record_item_addition(lecturer_id, item_id):
    """Record that a lecturer added an item"""
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        query = "INSERT INTO Adds (lecturerID, itemID) VALUES (%s, %s)"
        cursor.execute(query, (lecturer_id, item_id))
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        connection.close()
        raise e


def get_course_content(course_code):
    """Retrieve all content for a course organized by sections"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        query = """
            SELECT 
                s.sectionID,
                s.sectionName,
                si.itemID,
                si.itemName,
                si.itemType,
                si.content
            FROM Section s
            LEFT JOIN SectionItem si ON s.sectionID = si.sectionID
            WHERE s.courseCode = %s
            ORDER BY s.sectionID, si.itemID
        """
        cursor.execute(query, (course_code,))
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        
        # Organize data by sections
        sections = {}
        for row in rows:
            section_id = row['sectionID']
            if section_id not in sections:
                sections[section_id] = {
                    'sectionID': section_id,
                    'sectionName': row['sectionName'],
                    'items': []
                }
            
            if row['itemID']:
                sections[section_id]['items'].append({
                    'itemID': row['itemID'],
                    'itemName': row['itemName'],
                    'itemType': row['itemType'],
                    'content': row['content']
                })
        
        return list(sections.values())
    except Exception as e:
        connection.close()
        raise e


def get_section(section_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        query = "SELECT * FROM Section WHERE sectionID = %s"
        cursor.execute(query, (section_id,))
        section = cursor.fetchone()
        cursor.close()
        connection.close()
        return section
    except Exception as e:
        connection.close()
        raise e
