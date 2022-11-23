from flask import Flask
from flask import Flask, render_template, redirect, request, session, Response
from flask_session import Session
from helpers import login_required
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3


# Configure application
app = Flask(__name__)

# Auto-reloads templates if modified
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Unables permanent session so it has a timeout
app.config['SESSION_PERMANENT'] = False

# Stores the session in the system hard drive instead of cookies
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

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

'''
@app.route('/register', methods=['GET', 'POST'])
# Registers the user
def register():
    # When the site is opened via GET it gets displayed
    if request.method == "GET":
        return render_template("register.html")

    #else:
        
'''


@app.route('/login', methods=['GET', 'POST'])
def login():

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

        # Query database for username
        # rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return Response("invalid username and/or password", status=400,)
        
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

