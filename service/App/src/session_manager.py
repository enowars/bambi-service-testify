import uuid, mysql.connector

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


def get_new_session_id():
    return uuid.uuid4()


def create_session(username: str):
    uu = get_new_session_id()
