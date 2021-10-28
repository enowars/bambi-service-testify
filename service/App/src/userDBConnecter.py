import hashlib
import os

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


def create_user(username: str, password: bytes, email: str) -> bool:
    connector = get_connector()
    salt = os.urandom(32)
    key = get_hash(password, salt)
    cursor = connector.cursor()
    sql = "INSERT INTO user_database.users(username, password, salt, email) VALUES (%s, %s, %s, %s)"
    vals = (username, key, salt, email)
    try:
        cursor.execute(sql, vals)
    except mysql.connector.Error as err:
        print('User already in use {}'.format(err))
        return False
    connector.commit()
    return True


def check_user(username: str, password: bytes) -> bool:
    connector = get_connector()
    cursor = connector.cursor()

    sql = "SELECT password, salt FROM user_database.users WHERE username = %s"
    vals = (username,)

    cursor.execute(sql, vals)
    result = cursor.fetchone()
    if result is None:
        return False
    hash_db = bytes(result[0])
    salt_db = bytes(result[1])
    hash_comp = get_hash(password, salt_db)

    return True if hash_comp == hash_db else False


def get_hash(instr: bytes, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac('sha256', instr, salt, 100000)


def get_users():
    connector = get_connector()
    cursor = connector.cursor()

    sql = "SELECT username FROM user_database.users " \
        "WHERE username NOT LIKE 'doctor0_' ORDER BY user_id DESC LIMIT 2000"
    cursor.execute(sql, ())
    users = [row[0] for row in cursor.fetchall()]

    return users

