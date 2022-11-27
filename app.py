from flask import Flask
from flask import Flask, render_template, redirect, request, session, Response
from flask_session import Session
from helpers import login_required
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import re


# Configure application
app = Flask(__name__)

# Auto-reloads templates if modified
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Unables permanent session so it has a timeout
app.config['SESSION_PERMANENT'] = False

# Stores the session in the system hard drive instead of cookies
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# This function return dictionaries instead of tuples from the sql queries
def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

# Establishes connection with the database
con = sqlite3.connect("test.db")

# Have to assign dict_factory so that cursor iterates through the given dicts
con.row_factory = dict_factory

# Creating the cursor to execute SQL statements and fetch results
cur = con.cursor()

app.after_request
def after_request(response):
    #Disables catching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# The login_required decorator requires the user to login before use
#@login.required

@app.route('/')
#@login_required
def main_page():
    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
# Registers the user
def register():

    con = sqlite3.connect("test.db")
    cur = con.cursor()

    # When the site is opened via GET it gets displayed
    if request.method == "GET":
        return render_template("register.html")

    else:
        if not request.form.get("username"):
            return Response("Must provide username", status=400)

        elif not request.form.get("password"):
            return Response("Must provide password", status=400)

        elif validate(request.form.get("password")) == False:
            return Response("Password must contain at least 8 characters, a number and a capital letter!", 400)

        elif not request.form.get("confirmation"):
            return Response("Must confirm password", status=400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return Response("Passwords must match", status=400)
        
        # Stores the hased password and the username in the database
        hashed_password = generate_password_hash(request.form.get("password"))
        username = request.form.get("username")

        # Checks for username duplication
        try:
            new_user = cur.execute("INSERT INTO test (username, hash) VALUES (?, ?)", username, hashed_password)
            #print(new_user)
            con.commit()
        except:
            return Response("The username is already taken", status=400)

        session["user_id"] = new_user

        return redirect("/")

        
@app.route('/login', methods=['GET', 'POST'])
def login():

    con = sqlite3.connect("test.db")

    #Forgets the user
    session.clear()

     # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return Response(
                    "must provide username", 
                    status=400,)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return Response("must provide password", status=400,)

        #Query database for username (it gives back a cursor!)
        result = cur.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        
        for row in result:

        # Ensure username exists and password is correct
            if len(row) != 1 or not check_password_hash(row[0]["hash"], request.form.get("password")):
                return Response("invalid username and/or password", status=400,)
        
        # Remember which user has logged in
        session["user_id"] = row[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


def validate(password):

    # This functions checks if the password meets all the requirements
    if len(password) < 8:
        return False
    elif re.search('[0-9]', password) is None:
        return False
    elif re.search('[A-Z]', password) is None:
        return False

    return True