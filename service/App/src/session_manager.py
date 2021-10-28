import mysql.connector
import uuid

hostname = "testify-mysql"


def get_new_session_id():
    return uuid.uuid4()


def check_session_id(connector, session_id):
    cursor = connector.cursor()
    sql = "SELECT * FROM user_database.sessions WHERE session_id = %s"
    vals = (session_id,)
    cursor.execute(sql, vals)
    result = cursor.fetchone()
    return True if result else False


def delete_session(connector, session_id):
    cursor = connector.cursor()
    sql = "DELETE FROM user_database.sessions WHERE session_id = %s"
    vals = (session_id,)
    try:
        cursor.execute(sql, vals)
        connector.commit()
    except mysql.connector.Error as err:
        print('session to delete not found: {}'.format(err))


def create_session(connector, username: str) -> uuid:
    user_id = get_user_id_for_username(connector, username)
    if user_id != -1:
        uu = get_new_session_id()
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


def get_user_id_for_username(connector, username: str) -> int:
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


def get_user_name_for_session(connector, session_id):
    cursor = connector.cursor()
    sql = "SELECT user_database.users.username FROM user_database.users JOIN user_database.sessions s on users.user_id = s.user_id WHERE s.session_id = %s"
    vals = (session_id,)
    cursor.execute(sql, vals)
    result = cursor.fetchone()
    if result is None:
        print('Error user not found')
        return None
    else:
        return result[0]
