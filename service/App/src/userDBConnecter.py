import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database='company'
)

print(mydb)

mycursor = mydb.cursor()

mycursor.execute("SHOW COLUMNS FROM employees;")

for x in mycursor:
  print(x)
