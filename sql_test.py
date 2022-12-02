import sqlite3
from flask import Flask

'''
con = sqlite3.connect("tutorial.db")

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    
    return {key: value for key, value in zip(fields, row)}

con.row_factory = dict_factory

cur = con.cursor()

res = cur.execute("SELECT score FROM movie")
result = res.fetchall()
'''

import sqlite3

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}
'''
title = "Shrek"
year = 2011
score = 8.5

con = sqlite3.connect("tutorial.db")

con.row_factory = dict_factory

cur = con.cursor()

#cur.execute("INSERT INTO movie (title, year, score) VALUES (?, ?, ?)", (title, year, score))

con.commit()

results = cur.execute("SELECT title FROM movie")
for row in results:
    print(row)
'''
'''
results = res.fetchall
for row in results:
    print(row)
'''
#print(result)

username = "Test"

connection = sqlite3.connect("test.db")

connection.row_factory = dict_factory

cur = connection.cursor()

user_data = (cur.execute("SELECT * FROM users WHERE username = ?", (username,)))
user = user_data.fetchall()
print(user)



