import mysql.connector

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
            database='user_database'
        )
    return mydb


def get_user_id_for_session_id(session_id):
    connector = get_connector()
    cursor = connector.cursor()
    sql = "SELECT user_id FROM user_database.sessions WHERE session_id = %s"
    vals = (session_id,)
    cursor.execute(sql, vals)
    result = cursor.fetchone()
    if result is None:
        print('Error session not found')
        return -1
    else:
        return result[0]


def set_appointment(session_id: str, appointment):
    user_id = get_user_id_for_session_id(session_id)
    if user_id != -1:
        connector = get_connector()
        cursor = connector.cursor()
        sql = "INSERT INTO user_database.appointments(user_id, name, extra_info, date) VALUES (%d, %s, %s, %s)"
        vals = (appointment['user_id'], appointment['name'], appointment['extra_info']. appointment['date'])
        try:
            cursor.execute(sql, vals)
        except mysql.connector.Error as err:
            print('invalid appointment: {}'.format(err))
        connector.commit()


def get_appointment():
