# test_db.py
from app.config import Config
import mysql.connector

print("DB_USER:", Config.DB_USER)
print("DB_PASSWORD:", Config.DB_PASSWORD)

conn = mysql.connector.connect(
    host=Config.DB_HOST,
    port=Config.DB_PORT,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD,
    database=Config.DB_NAME
)
print("Connected!")
conn.close()