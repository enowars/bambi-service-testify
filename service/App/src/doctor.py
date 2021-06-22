import mysql.connector

hostname = "testify-mysql"


def get_connector():
    global hostname
    mydb = mysql.connector.connect(
        host=hostname,
        user="root",
        password="root",
    )
    return mydb


def check_doctor(username: str) -> bool:
    connector = get_connector()
    cursor = connector.cursor()
    cursor.execute(
        "SELECT IF ((SELECT * FROM user_database.doctor_appointments "
        "WHERE user_database.doctor_appointments.user_id = "
        "(SELECT user_id FROM user_database.users WHERE username = %s))"
        "OR (SELECT user_database.users.is_doctor), 1, 0)",
        (username,))
    res = cursor.fetchone()
    return True if res else False


def get_patient_info(search_user: str):
    connector = get_connector()
    cursor = connector.cursor()
    cursor.execute(
        "SELECT doctor, extra_info FROM user_database.appointments JOIN user_database.users "
        "ON users.user_id = appointments.user_id "
        "WHERE username = %s",
        (search_user,))
    res = cursor.fetchall()
    return res


