import mysql.connector
import uuid

mydb = None
hostname = "testify-mysql"


def get_connector():
    global mydb
    global hostname
    if mydb is None:
        mydb = mysql.connector.connect(
            host=hostname,
            user="root",
            password="root",
        )
    return mydb


def get_new_session_id():
    return uuid.uuid4()


def create_session(username: str) -> uuid:
    user_id = get_user_id_for_username(username)
    if user_id != -1:
        uu = get_new_session_id()
        connector = get_connector()
        cursor = connector.cursor()
        sql = "INSERT INTO user_database.sessions(session_id, user_id) VALUES (%s, %s)"
        vals = (str(uu), user_id)
        try:
            cursor.execute(sql, vals)
        except mysql.connector.Error as err:
            print('session id already in use: {}'.format(err))
            return None
        connector.commit()
        return uu
    return -1


def get_user_id_for_username(username: str) -> int:
    connector = get_connector()
    cursor = connector.cursor()
    sql = "SELECT user_database.users.user_id FROM user_database.users WHERE username = %s"
    vals = (username,)
    cursor.execute(sql, vals)
    result = cursor.fetchone()
    if result is None:
        print('Error user not found')
        return -1
    else:
        return result[0]
