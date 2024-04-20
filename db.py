import mysql.connector
import config




def connect_to_mysql():
    """
    Connects to a MySQL database and returns a connection object.

    Returns:
        A MySQL connection object.
    """

    # Replace the values en config.py with your own MySQL credentials.
    host = config.MYSQL_HOST
    user = config.MYSQL_USER
    password = config.MYSQL_PASSWORD
    database = config.MYSQL_DATABASE

    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
