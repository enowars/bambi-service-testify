import os.path

import mysql.connector
from werkzeug.utils import secure_filename

hostname = "testify-mysql"


def get_user_id_for_session_id(connector, session_id):
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


def set_appointment(connector, session_id: str, appointment, file) -> int:
    user_id = get_user_id_for_session_id(connector, session_id)
    if user_id != -1:
        cursor = connector.cursor()
        sql = "INSERT INTO user_database.appointments(user_id, name, extra_info, date, filename, doctor, pin) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        filename = appointment['filename'].replace('/', '')
        if ".." in filename:
            filename = filename.split("..")[-1]
        vals = (user_id, appointment['name'], appointment['extra_info'], appointment['date'] + ' ' +
                appointment['time'], filename, appointment['doctor'], appointment['pin'])
        try:
            cursor.execute(sql, vals)
            path = "userdata/" + secure_filename(filename)
            if file and not os.path.exists(path):
                file.save(path)
            connector.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print('invalid appointment: {}'.format(err))


def get_appointments(connector, session_id: str):
    user_id = get_user_id_for_session_id(connector, session_id)
    cursor = connector.cursor()
    sql = "SELECT name, extra_info, date, appointment_id FROM user_database.appointments WHERE user_id = %s ORDER BY appointment_id DESC"
    vals = (user_id,)
    cursor.execute(sql, vals)
    result = cursor.fetchall()
    if result is None:
        print('no appointments found')
    return get_card_format(result)


def get_id_file(connector, session_id: str, appointment_id: int):
    cursor = connector.cursor()
    sql = "SELECT a.filename FROM user_database.appointments a " \
          "JOIN user_database.sessions s ON a.user_id = s.user_id " \
          "WHERE s.session_id = %s AND a.appointment_id = %s"
    vals = (session_id, appointment_id)
    cursor.execute(sql, vals)
    result = cursor.fetchone()
    if result:
        return "userdata/" + result[0]
    else:
        print("appointment id and session id do not match")
        return None


def get_info(connector, appid, pin):
    cursor = connector.cursor()
    sql = "SELECT extra_info FROM user_database.appointments WHERE appointment_id = %s AND pin = %s"
    vals = (appid, pin)
    cursor.execute(sql, vals)
    result = cursor.fetchone()
    return result[0] if result else None


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
