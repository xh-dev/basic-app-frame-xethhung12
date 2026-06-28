import mysql.connector
from mysql.connector import Error

def connect(
    host: str,
    user: str,
    password: str,
    database: str
) -> mysql.connector.connection.MySQLConnection:
    try:
        # 1. Establish the connection to the server
        connection = mysql.connector.connect(
            host=host,       # Use IP address if database is hosted online
            user=user,    # Default username is usually 'root'
            password=password,# Password assigned during MySQL installation
            database=database # Name of the target database
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
