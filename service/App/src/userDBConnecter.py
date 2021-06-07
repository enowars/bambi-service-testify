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


def get_hash(string, salt):
    if isValid(string):
        return hashlib.pbkdf2_hmac('sha256', string, salt, 100000)
    else:
        return string


def isValid(password) -> bool:
    try:
        pw = password.decode('utf-8')
    except UnicodeError as e:
        return False
    return all(32 < ord(c) < 127 for c in pw)
