import hashlib
import os

import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database='user_database'
)


def create_user(username : str, password : str) -> bool:
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    cursor = mydb.cursor()
    sql = "INSERT INTO users(username, password, salt) VALUES (%s, %s, %s)"
    vals = (username, key, salt)
    try:
        cursor.execute(sql, vals)
    except mysql.connector.Error as err:
        print('User already in use {}'.format(err))
        return False
    mydb.commit()
    return True


def check_user(username : str, password : str) -> bool:
    cursor = mydb.cursor()

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





