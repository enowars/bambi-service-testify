import os.path

import mysql.connector
from werkzeug.utils import secure_filename

hostname = "testify-mysql"


def get_connector():
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


def set_appointment(session_id: str, appointment, file) -> int:
    user_id = get_user_id_for_session_id(session_id)
    if user_id != -1:
        connector = get_connector()
        cursor = connector.cursor()
        sql = "INSERT INTO user_database.appointments(user_id, name, extra_info, date, filename) " \
              "VALUES (%s, %s, %s, %s, %s)"
        path = get_path(appointment['filename']) if file else None
        vals = (user_id, appointment['name'], appointment['extra_info'], appointment['date'] + ' ' +
                appointment['time'], path)
        try:
            cursor.execute(sql, vals)
            if file:
                file.save('user_data/ids/' + secure_filename(appointment['filename']))
            connector.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print('invalid appointment: {}'.format(err))


def get_appointments(session_id: str):
    user_id = get_user_id_for_session_id(session_id)
    connector = get_connector()
    cursor = connector.cursor()
    sql = "SELECT name, extra_info, date, appointment_id FROM user_database.appointments WHERE user_id = %s ORDER BY appointment_id DESC"
    vals = (user_id,)
    cursor.execute(sql, vals)
    result = cursor.fetchall()
    if result is None:
        print('no appointments found')
    return get_card_format(result)


def get_path(path: str):
    if path:
        basedir = os.path.abspath("user_data/")
        path_comp = 'user_data/ids/' + path
        matchpath = os.path.abspath(path_comp)
        if matchpath.startswith(basedir) and basedir == os.path.commonpath((basedir, matchpath)):
            return os.path.abspath('user_data/ids/' + path)
    return None


def get_id_file(session_id: str, appointment_id: int):
    connector = get_connector()
    cursor = connector.cursor()
    sql = "SELECT a.filename FROM user_database.appointments a " \
          "JOIN user_database.sessions s ON a.user_id = s.user_id " \
          "WHERE s.session_id = %s AND a.appointment_id = %s"
    vals = (session_id, appointment_id)
    cursor.execute(sql, vals)
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        print("appointment id and session id do not match")
        return None


def get_card_format(result):
    cards = []
    for r in result:
            cards.append({
                'name': r[0],
                'info': r[1],
                'date': r[2].strftime('%Y-%m-%d / %H:%M'),
                'id': str(r[3])
            })
    return cards
