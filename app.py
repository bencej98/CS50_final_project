from flask import Flask
from flask import Flask, render_template, redirect, request, session, Response
from flask_session import Session
from helpers import login_required, usd, validate
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

# Imports custom filter for dollars
app.jinja_env.filters["usd"] = usd

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

        # Checks for username duplication
        cur.execute(   """
                          SELECT *
                          FROM users
                          WHERE username = ?
                          """
                          , (username,))
        validator = cur.fetchone()
        if validator is not None:
            return Response("This username is already taken", status=400)
        
        # Stores the hased password and the username in a variable
        hashed_password = generate_password_hash(password)
        cur.execute(      """
                          INSERT INTO users (username, hash)
                          VALUES (?, ?)
                          """
                          , (username, hashed_password))

        connection.commit()

        # Sets session with the current user id
        user_data = (cur.execute(      """
                                       SELECT * 
                                       FROM users
                                       WHERE username = ?
                                       """
                                       , (username,)))
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
        user_data = cur.execute( """
                                    SELECT * 
                                    FROM users
                                    WHERE username = ?
                                    """ 
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

@app.route('/')

# The login_required decorator requires the user to login before use
@login_required
def main_page():
    
    if request.method == "GET":
        # Sets up db connection and cursors (dict_factory is to return a dictionary not a tuple)
        connection = sqlite3.connect("testDB.db")
        connection.row_factory = dict_factory
        cur = connection.cursor()
        # Gets current logged in user
        user_data = cur.execute(   """
                                    SELECT username
                                    FROM users
                                    WHERE id = ?
                                    """
                                    ,(session["user_id"],))
                          
        user = user_data.fetchall()
        username = user[0]["username"]

        # Gets data neccessarry for main_page
        dashboard_data = cur.execute(   """
                                        SELECT possession_type, amount
                                        FROM all_assets
                                        WHERE username = ?
                                        """
                                        , (username,))

        dashboard = dashboard_data.fetchall()

        # Gets the curent total value of all the assets
        total_value = 0
        for data in dashboard:
            total_value += int(data["amount"])
        
        # Seting all values the zero beforehand because otherwise if amount is not present the function crashes
        cash_amount = 0
        asset_amount = 0
        bank_account_amount = 0
        credit_amount = 0

        # Gets all the amounts from the database ( I should find a better method for this)
        for data in dashboard:
            if data["possession_type"] == "Cash" :
                cash_amount = data["amount"]
            elif data["possession_type"] == "Asset" :
                asset_amount = data["amount"]
            elif data["possession_type"] == "Bank Account" :
                bank_account_amount = data["amount"]
            else:
                credit_amount = data["amount"]

        connection.close()

    # This looks ugly and should fix it with some better method as well
    return render_template("main_page.html", credit_amount = credit_amount ,total_value=total_value, cash_amount=cash_amount, asset_amount=asset_amount , bank_account_amount=bank_account_amount, )

@app.route("/transactions", methods=['GET', 'POST'])
@login_required
def transaction():

# This function lets the user to withdraw or deposit assets of many types

    # Sets up db connection and cursors (dict_factory is to return a dictionary not a tuple)
    connection = sqlite3.connect("testDB.db")
    connection.row_factory = dict_factory
    cur = connection.cursor()

    # Gets user data
    user_data = cur.execute(    """
                                SELECT username
                                FROM users
                                WHERE id = ?
                                """
                                , (session["user_id"],))

    user = user_data.fetchall()
    username = user[0]["username"]

    if request.method == "GET":
        return render_template("transactions.html")

    # Checks for possible errors
    if not request.form.get("transaction"):
        return Response("Must provide transaction type", status=400,)
    elif not request.form.get("amount"):
        return Response("Must provide the amount of money for transaction", status=400,)
    elif int(request.form.get("amount")) <= 0: 
        return Response("Must provide a positive integer", status=400,)
    elif not request.form.get("possession"):
        return Response("Must provide type of posession",status=400,)


    transaction_type = request.form.get("transaction")
    possession_type = request.form.get("possession")
    amount = int(request.form.get("amount"))

    # Validation is to check whether is there a similar entry or not with the given transaction type
    validation = cur.execute(   """
                                SELECT id
                                FROM all_assets WHERE username = ?
                                AND possession_type = ?
                                AND transaction_type = ? 
                                """
                                , (username, possession_type, "Deposit",))

    count = len(validation.fetchall())

    # Records the transaction data in the transactions (needed for reports) and all_assets table (needed for index) 
    if request.form.get("transaction") == "Deposit":
        cur.execute(    """
                        INSERT INTO transactions (username, transaction_type, possession_type, amount)
                        VALUES (?, ?, ?, ?)
                        """
                        , (username, transaction_type, possession_type, amount,))
        # If there is no entry yet inserts the given data
        if count == 0 :
            cur.execute(    """
                            INSERT INTO all_assets (username, transaction_type, possession_type, amount)
                            VALUES (?, ?, ?, ?)
                            """
                            , (username, transaction_type, possession_type, amount,))
        # If entry already exists updates the given data
        else:
            cur.execute(    """
                            UPDATE all_assets 
                            SET amount = amount + ?
                            WHERE username = ? 
                            AND possession_type = ?
                            AND transaction_type = ? 
                            """
                            , (amount, username, possession_type, transaction_type,))
        connection.commit()

    elif request.form.get("transaction") == "Withdraw":
        cash = cur.execute( """
                            SELECT amount 
                            FROM all_assets 
                            WHERE username = ? 
                            AND possession_type = ? 
                            AND transaction_type = ? 
                            """
                            , (username, possession_type, "Deposit",))
        cash_count = cash.fetchall()
        # If there is no entry yet inserts the given data
        if count == 0:
                return Response("Amount can't be higher than asset amou", status=400)
        # Checks if the user has enough assets and acts based on that
        elif cash_count[0]["amount"] <= amount:
                return Response("Amount can't be higher than asset amount", status=400)
        elif cash_count[0]["amount"] >= amount:
            cur.execute(    """
                            INSERT INTO transactions (username, transaction_type, possession_type, amount) 
                            VALUES (?, ?, ?, ?)
                            """
                            , (username, transaction_type, possession_type, amount,))

            cur.execute(    """
                            UPDATE all_assets 
                            SET amount = amount - ? 
                            WHERE username = ? 
                            AND possession_type = ? 
                            AND transaction_type = ? 
                            """
                            , (amount, username, possession_type, "Deposit",))

        connection.commit()

    connection.close()
    return redirect("/")

@app.route("/reports")
@login_required
def reports():
# This functions return the reports of all transactions made from an account

# Sets up connection with db, creates a cursor
    connection = sqlite3.connect("testDB.db")
    connection.row_factory = dict_factory
    cur = connection.cursor()

    # Gets current user's id
    user_data = cur.execute(    """
                                SELECT username
                                FROM users
                                WHERE id = ?
                                """
                                ,(session["user_id"],))

    # Returns current user's data needed for the report
    user = user_data.fetchall()
    username = user[0]["username"]
    
    cursor = cur.execute(   """
                            SELECT transaction_type, possession_type, amount, date 
                            FROM transactions 
                            WHERE username = ?
                            """
                            , (username,))

    reports = cursor.fetchall()
    connection.close()
    return render_template("reports.html", reports=reports)


if __name__ == '__main__':
    app.run(debug=True)