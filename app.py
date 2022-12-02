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
con = sqlite3.connect('testDB.db')

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

    connection = sqlite3.connect("testDB.db")
    connection.row_factory = dict_factory
    cur = connection.cursor()
    # When the site is opened via GET it gets displayed
    if request.method == "GET":
        return render_template("register.html")

    else:
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return Response("Must provide username", status=400)

        elif not password:
            return Response("Must provide password", status=400)

        elif validate(password) == False:
            return Response("Password must contain at least 8 characters, a number and a capital letter!", status=400)

        elif not request.form.get("confirmation"):
            return Response("Must confirm password", status=400)

        elif password != request.form.get("confirmation"):
            return Response("Passwords must match", status=400)

        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        validator = cur.fetchone()
        if validator is not None:
            return Response("This username is already taken", status=400)
        
        # Stores the hased password and the username in a variable
        hashed_password = generate_password_hash(password)
        cur.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hashed_password))
        connection.commit()
        # Checks for username duplication
        '''
        try:
            cur.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hashed_password))
            connection.commit()

        except:
            return Response("The username is already taken", status=400)
        '''
        # Sets session with the current user id
        user_data = (cur.execute("SELECT * FROM users WHERE username = ?", (username,)))
        user = user_data.fetchall()
        session["user_id"] = (user[0]["id"])
        connection.close()
        return redirect("/")

        
@app.route('/login', methods=['GET', 'POST'])

# Logs in the user
def login():

    #Forgets the user
    session.clear()

    connection = sqlite3.connect("testDB.db")
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
        user_data = cur.execute("""SELECT * 
                                    FROM users
                                    WHERE username = ?""" 
                                    , (request.form.get("username"),))
        user = user_data.fetchall()

        if not any(user):
            return Response("Username doesn't exist", status=400)
        elif check_password_hash(user[0]["hash"], (request.form.get("password"))) != True:
            return Response("Invalid username and/or password", status=400,)
 
        # Remember which user has logged in
        session["user_id"] = user[0]["id"]
        
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

@app.route("/transactions", methods=['GET', 'POST'])
@login_required
def transaction():

    connection = sqlite3.connect("testDB.db")
    connection.row_factory = dict_factory
    cur = connection.cursor()


    user = cur.execute("""SELECT username
                          FROM users
                          WHERE id = ?"""
                          ,(session["user_id"],))
    for row in user:
        username = row["username"]

    if request.method == "GET":
        return render_template("transactions.html")
    
    if not request.form.get("transaction"):
        return Response("Must provide transaction type", status=400,)
    elif not request.form.get("amount"):
        return Response("Must provide the amount of money for transaction", status=400,)
    elif int(request.form.get("amount")) <= 0: 
        return Response("Must provide a positive integer", status=400,)
    elif not request.form.get("possession"):
        return Response("Must provide type of posession",status=400,)

    # Also have to check if there is enough money on the account

    transaction_type = request.form.get("transaction")
    possession_type = request.form.get("possession")
    amount = int(request.form.get("amount"))
    validation = cur.execute("SELECT id FROM all_assets WHERE username = ? AND possession_type = ? AND transaction_type = ? ", (username, transaction_type, possession_type,))
    count = len(validation.fetchall())
    # Records the transaction data in the transactions (needed for reports) and all_assets table (needed for index) 
    if request.form.get("transaction") == "Deposit":
        cur.execute("INSERT INTO transactions (username, transaction_type, possession_type, amount) VALUES (?, ?, ?, ?)", (username, transaction_type, possession_type, amount,))
        # Here I should check whether the user transaction type and possession type is already present at the table
        if count == 0 :
            cur.execute("INSERT INTO all_assets (username, transaction_type, possession_type, amount) VALUES (?, ?, ?, ?)", (username, transaction_type, possession_type, amount,))
        else:
            cur.execute("UPDATE all_assets SET amount = amount + ? WHERE username = ? AND possession_type = ? AND transaction_type = ? ", (amount, username, transaction_type, possession_type,))
        connection.commit()
    elif request.form.get("transaction") == "Withdraw":
        cash = cur.execute("SELECT amount FROM all_assets WHERE username = ? AND possession_type = ? AND transaction_type = ? ", (username, possession_type, transaction_type,))
        cash_count = cash.fetchall()
        if count == 0 and cash_count[0]["amount"] >= int(request.form.get("amount")):
            cur.execute("INSERT INTO transactions (username, transaction_type, possession_type, amount) VALUES (?, ?, ?, ?)", (username, transaction_type, possession_type, amount,))
        else:
            if cash_count[0]["amount"] >= int(request.form.get("amount")):
                cur.execute("UPDATE all_assets SET amount = amount - ? WHERE username = ? AND possession_type = ? AND transaction_type = ? ", (amount, username, transaction_type, possession_type,))
            else:
                return Response("Amount can't be higher than asset amount", status=400)
        connection.commit()

    connection.close()
    return redirect("/")


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