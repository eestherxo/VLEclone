import os
from dotenv import load_dotenv
import mysql.connector
from urllib.parse import urlparse


load_dotenv()

db_url = urlparse(os.getenv("DB_URL"))


def get_connection():
    connection = mysql.connector.connect(
        host=db_url.hostname,
        user=db_url.username,
        password=db_url.password,
        database=db_url.path[1:],
        port=db_url.port
    )
    return connection