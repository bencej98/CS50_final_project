from flask import redirect, render_template, request, session, Flask
from functools import wraps
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import re
import sqlite3

# Login Required Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# Format amount as USD
def usd(amount):
    return f"${amount:,.2f}"

 # This functions checks if the password meets all the requirements
def validate(password):

    if len(password) < 8:
        return False
    elif re.search('[0-9]', password) is None:
        return False
    elif re.search('[A-Z]', password) is None:
        return False

    return True

# This function return dictionaries instead of tuples from the sql queries
def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

#This function creates and admin user or checks if there is already one
def admin():
    connection = sqlite3.connect("testDB.db")

    connection.row_factory = dict_factory

    cur = connection.cursor()
    admin_user = cur.execute("SELECT username FROM users WHERE id = 1")
    admin_user_data = admin_user.fetchall()
    admin_username = "admin"
    admin_password = "admin"

    if not admin_user_data:

        hashed_password = generate_password_hash(admin_password)
        cur.execute("INSERT INTO users (id, username, hash) VALUES (1, ?, ?)", (admin_username, hashed_password))
        connection.commit()
        connection.close()
        return True
    else:
        return True