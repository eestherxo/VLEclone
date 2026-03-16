from app.db import get_connection
from bcrypt import hashpw, gensalt, checkpw

def verify_user(user_id, password):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT userID, firstName, lastName, role FROM User WHERE userID = %s"
    cursor.execute(query, (user_id, password))
    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if not user:
        return None
    
    if checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return user
    
    # Plain text comparison for dummy data
    if user['password'] == password:
        return user

    return None

def insert_user(user_id, first_name, last_name, password, role):
    connection = get_connection()
    cursor = connection.cursor()

    hashed_password = hashpw(password.encode('utf-8'), gensalt())

    query = "INSERT INTO User (userID, firstName, lastName, password, role) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (user_id, first_name, last_name, hashed_password.decode('utf-8'), role))

    if role.lower() == "admin":
        cursor.execute("INSERT INTO Admin (adminID) VALUES (%s)", (user_id,))
    elif role.lower() == "student":
        cursor.execute("INSERT INTO Student (studentID) VALUES (%s)", (user_id,))
    elif role.lower() == "lecturer":
        cursor.execute("INSERT INTO Lecturer (lecturerID) VALUES (%s)", (user_id,))

    connection.commit()
    cursor.close()
    connection.close()
    

def get_user(user_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT userID, firstName, lastName, role FROM User WHERE userID = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()

    cursor.close()
    connection.close()
    return user



