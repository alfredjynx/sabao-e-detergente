import mysql.connector

db = mysql.connector.connect(
    host="mysql",
    user="root",
    password="root",
    database="bubble"
)
cursor = db.cursor()
