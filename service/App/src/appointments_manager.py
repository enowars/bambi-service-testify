import mysql.connector

mydb = None
hostname = "testify-mysql"


def get_connector():
    global mydb
    global hostname
    mydb = mysql.connector.connect(
        host=hostname,
        user="root",
        password="root"
    )
    return mydb


def get_user_id_for_session_id(session_id):
    connector = get_connector()
    cursor = connector.cursor()
    sql = "SELECT user_database.sessions.user_id FROM user_database.sessions WHERE session_id = %s"
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
        sql = "INSERT INTO user_database.appointments(user_id, name, extra_info, date) VALUES (%s, %s, %s, %s)"
        vals = (user_id, appointment['name'], appointment['extra_info'], appointment['date'] + ' ' + appointment['time'])
        try:
            cursor.execute(sql, vals)
        except mysql.connector.Error as err:
            print('invalid appointment: {}'.format(err))
        connector.commit()


def get_appointments(session_id: str):
    user_id = get_user_id_for_session_id(session_id)
    connector = get_connector()
    cursor = connector.cursor()
    sql = "SELECT name, extra_info, date FROM user_database.appointments WHERE user_id = %s"
    vals = (user_id,)
    cursor.execute(sql, vals)
    result = cursor.fetchall()
    if result is None:
        print('no appointments found')
    else:
        print(result)
    return get_card_format(result)


def get_card_format(result):
    cards = []
    for r in result:
            cards.append({
                'name': r[0],
                'info': r[1],
                'date': r[2].strftime('%d.%m.%Y %H:%M')
            })
    return cards
