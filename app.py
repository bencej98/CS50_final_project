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
con = sqlite3.connect('test.db')

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


@app.route('/')

# The login_required decorator requires the user to login before use
@login_required
def main_page():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])

# Registers the user
def register():

    connection = sqlite3.connect("test.db")
    connection.row_factory = dict_factory
    cur = connection.cursor()
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
        
        # Stores the hased password and the username in a variable
        hashed_password = generate_password_hash(request.form.get("password"))
        username = request.form.get("username")

        # Checks for username duplication
        try:
            cur.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hashed_password))
            con.commit()
            con.close()
        except:
            return Response("The username is already taken", status=400)

        # Sets session with the current user id
        user_data = cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        session["user_id"] = user_data["id"]

        return redirect("/")

        
@app.route('/login', methods=['GET', 'POST'])

# Logs in the user
def login():

    #Forgets the user
    session.clear()

    connection = sqlite3.connect("test.db")
    connection.row_factory = dict_factory
    cur = connection.cursor()

     # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return Response(
                    "Must provide username", 
                    status=400,)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return Response("Must provide password", status=400,)

        #Query database for username (it gives back a cursor!)
        result = cur.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        
        '''
        for row in result:
            if check_password_hash(row["hash"], (request.form.get("password"))) != True:
                print("Password is not the same")
            print(row["hash"])
        '''
        #for row in result:
            #print(row[0]["hash"])
        
        for row in result:
        # Ensure username exists and password is correct
            session["user_id"] = row["id"]
            if row["username"] != request.form.get("username") or check_password_hash(row["hash"], (request.form.get("password"))) != True:
                return Response("Invalid username and/or password", status=400,)
            
        # Remember which user has logged in
        session["user_id"] = row["id"]
        
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    

@app.route("/logout")

# Logs out the user
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/transactions")
@login_required
def transaction():
    if request.method == "GET":
        return render_template("transactions.html")



 # This functions checks if the password meets all the requirements
def validate(password):

    if len(password) < 8:
        return False
    elif re.search('[0-9]', password) is None:
        return False
    elif re.search('[A-Z]', password) is None:
        return False

    return True

if __name__ == '__main__':
    app.run(debug=True)