import mysql.connector

hostname = "testify-mysql"


def get_username_for_email(connector, email: str) -> str:
    cursor = connector.cursor()
    sql = 'SELECT u.username FROM user_database.users u WHERE u.email = %s'
    vals = (email,)
    cursor.execute(sql, vals)
    result = cursor.fetchone()
    if result:
        return result[0]

