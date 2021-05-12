import mysql.connector

hostname = "testify-mysql"


def get_connector():
    global hostname
    mydb = mysql.connector.connect(
        host=hostname,
        user="usertable_user",
        password="userpass",
    )
    return mydb


def get_username_for_email(email: str) -> str:
    connector = get_connector()
    cursor = connector.cursor()
    sql = """SELECT u.username FROM user_database.users u WHERE u.email = '%s'""" % email
    sql2 = 'SELECT u.username FROM user_database.users u WHERE u.email = \'\';SELECT * FROM user_database.users; -- \''
    iterator = cursor.execute(sql, multi=True)
    result = None
    for i in iterator:
        result = i.fetchall()
    if result:
        res = ""
        for t in result:
            for e in t:
                res += e
        return res
    else:
        return None

