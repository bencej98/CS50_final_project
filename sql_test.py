import sqlite3
from flask import Flask
import sqlite3

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

#print(result)

username = "Test"
possession_type = "Cash"
transaction_type = "Deposit"
connection = sqlite3.connect("testDB.db")

connection.row_factory = dict_factory

cur = connection.cursor()

validation = cur.execute("SELECT id FROM all_assets WHERE username = ? AND possession_type = ? AND transaction_type = ? ", (username, possession_type, transaction_type,))
count = len(validation.fetchall())
print(count)



