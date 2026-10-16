from database import get_db_connection

connection = get_db_connection()

if connection:
    print("Database test successful!")

    cursor = connection.cursor()

    cursor.execute("SELECT DATABASE()")
    print("Database:", cursor.fetchone())

    cursor.execute("SHOW TABLES")
    print("Tables:", cursor.fetchall())

    cursor.close()
    connection.close()
else:
    print("Database test failed!")