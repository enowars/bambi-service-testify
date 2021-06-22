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
    cursor.execute("SELECT IF ((SELECT is_doctor FROM user_database.users WHERE username = %s) OR (SELECT "
                   "EXISTS(SELECT * FROM user_database.appointments WHERE user_database.appointments.doctor = "
                   "%s)), 1, 0)", (username, username))
    res = cursor.fetchone()
    return True if res[0] == 1 else False


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


