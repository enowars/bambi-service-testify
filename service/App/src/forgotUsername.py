import mysql.connector

hostname = "testify-mysql"


def get_connector():
    global hostname
    mydb = mysql.connector.connect(
        host=hostname,
        user="usertable_user",
        password="userpass",
    )
    return mydb


def get_username_for_email(email: str) -> str:
    connector = get_connector()
    cursor = connector.cursor()
    sql = 'SELECT u.username FROM user_database.users u WHERE u.email = %s'
    vals = (email,)
    cursor.execute(sql, vals)
    result = cursor.fetchone()
    if result:
        return result[0]

