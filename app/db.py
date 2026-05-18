import os
from dotenv import load_dotenv
import mysql.connector


load_dotenv()

config = {
    "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY"),
    "DB_HOST": os.getenv("DB_HOST"),
    "DB_USER": os.getenv("DB_USER"),
    "DB_PASSWORD": os.getenv("DB_PASSWORD"),
    "DB_NAME": os.getenv("DB_NAME"),
}


def get_connection():
    connection = mysql.connector.connect(
        host=config["DB_HOST"],
        user=config["DB_USER"],
        password=config["DB_PASSWORD"],
        database=config["DB_NAME"]
    )
    return connection