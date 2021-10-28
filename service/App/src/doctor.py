import mysql.connector

hostname = "testify-mysql"


def get_connector():
    global hostname
    mydb = mysql.connector.connect(
        host=hostname,
        user="root",
        password="root",
        use_pure=True
    )
    return mydb


def check_doctor(username: str) -> bool:
    connector = get_connector()
    cursor = connector.cursor()
    cursor.execute("SELECT EXISTS(SELECT 1 FROM user_database.users WHERE user_database.users.username = %s "
            "AND user_database.users.is_doctor = TRUE) OR EXISTS(SELECT 1 FROM user_database.appointments "
            "WHERE user_database.appointments.doctor = %s)", (username, username))
    res = cursor.fetchone()
    return res[0] == 1


def get_patient_info(search_user: str):
    connector = get_connector()
    cursor = connector.cursor()
    cursor.execute("SELECT doctor, extra_info FROM user_database.appointments JOIN user_database.users "
        "ON users.user_id = appointments.user_id "
        "WHERE username = %s", (search_user,))
    res = cursor.fetchall()
    return res


