import hashlib
import os

import mysql.connector

mydb = None


def get_connector():
    global mydb
    if mydb is None:
        mydb = mysql.connector.connect(
            host="testify-mysql",
            user="root",
            password="root",
            database='user_database'
        )
    return mydb


def create_user(username : str, password : str) -> bool:
    connector = get_connector()
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
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


def check_user(username : str, password : str) -> bool:
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
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)





