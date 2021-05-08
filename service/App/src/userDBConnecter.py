import hashlib
import os

import mysql.connector

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


def create_user(username: str, password: bytes) -> bool:
    connector = get_connector()
    salt = os.urandom(32)
    key = get_hash(password, salt)
    cursor = connector.cursor()
    sql = "INSERT INTO users(username, password, salt) VALUES (%s, %s, %s)"
    vals = (username, key, salt)
    try:
        cursor.execute(sql, vals)
    except mysql.connector.Error as err:
        print('User already in use {}'.format(err))
        return False
    connector.commit()
    return True


def set_hostname(host: str):  # for debugging purposes
    global hostname
    hostname = host


def check_user(username: str, password: bytes) -> bool:
    connector = get_connector()
    cursor = connector.cursor()

    sql = "SELECT password, salt FROM users WHERE username = %s"
    vals = (username,)

    cursor.execute(sql, vals)
    result = cursor.fetchone()
    if result is None:
        return False
    hash_db = bytes(result[0])
    salt_db = bytes(result[1])
    hash_comp = get_hash(password, salt_db)

    return True if hash_comp == hash_db else False


def get_hash(password, salt):
    if checkASCII(password):
        return hashlib.pbkdf2_hmac('sha256', password, salt, 100000)
    else:
        print("error! password not valid ascii!")
        return password


def checkASCII(password) -> bool:
    try:
        pw = password.decode('utf-8')
    except UnicodeError as e:
        print("error! password not valid ascii!")
        return False
    return all(32 < ord(c) < 127 for c in pw)
