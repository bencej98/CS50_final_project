from flask import Flask
from flask import Flask, render_template, redirect, request, session, Response, flash
from flask_session import Session
from helpers import login_required, usd, validate, admin, dict_factory
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import re
from os import path


# Configure application
app = Flask(__name__)

ROOT = path.dirname(path.realpath(__file__))

# Auto-reloads templates if modified
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Unables permanent session so it has a timeout
app.config['SESSION_PERMANENT'] = False

# Stores the session in the system hard drive instead of cookies
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Imports custom filter for dollars
app.jinja_env.filters["usd"] = usd

#Validates the admin user
admin()

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

    # Establishes connection with the database
    connection = sqlite3.connect("testDB.db")

    # Have to assign dict_factory so that cursor iterates through the given dicts
    connection.row_factory = dict_factory

    # Creating the cursor to execute SQL statements and fetch results
    cur = connection.cursor()

    # When the site is opened via GET it gets displayed
    if request.method == "GET":
        return render_template("register.html")

    else:
        username = request.form.get("username")
        password = request.form.get("password")

        # Checks for possible errors 
        if not username:
            flash("Must provide username!")
            return render_template("register.html")
         
        elif not re.match("^[A-Za-z0-9]*$", username):
            flash("Username must only contain numbers and letters!")
            return render_template("register.html")

        elif not password:
            flash("Must provide password!")
            return render_template("register.html")

        elif validate(password) == False:
            flash("Password must contain at least 8 characters, a number and a capital letter!")
            return render_template("register.html")

        elif not request.form.get("confirmation"):
            flash("Must confirm password!")
            return render_template("register.html")

        elif password != request.form.get("confirmation"):
            flash("Passwords must match!")
            return render_template("register.html")


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
            flash("Must provide username!")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password!")
            return render_template("login.html")

        #Query database for username (it gives back a cursor!)
        user_data = cur.execute( """
                                    SELECT * 
                                    FROM users
                                    WHERE username = ?
                                    """ 
                                    , (request.form.get("username"),))
        user = user_data.fetchall()

        if not any(user):
            flash("Username doesn't exist!")
            return render_template("login.html")
        elif check_password_hash(user[0]["hash"], (request.form.get("password"))) != True:
            flash("Invalid username and/or password!")
            return render_template("login.html")
 
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
# This function gets data about different assets and displays it on the main page
def main_page():


    if request.method == "GET":

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

        # New query for only one database to get the data necessary for homepage dashboard
        dashboard_data = cur.execute(   """
                                        SELECT possession_type, amount
                                        FROM transactions
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
                cash_amount += data["amount"]
            elif data["possession_type"] == "Asset" :
                asset_amount += data["amount"]
            elif data["possession_type"] == "Bank Account" :
                bank_account_amount += data["amount"]
            else:
                credit_amount += data["amount"]

        connection.close()

    return render_template("main_page.html", credit_amount=credit_amount ,
                                             total_value=total_value, cash_amount=cash_amount,
                                             asset_amount=asset_amount , bank_account_amount=bank_account_amount,
                                             username=username)

@app.route("/transactions", methods=['GET', 'POST'])
@login_required
# This function lets the user to withdraw or deposit assets of many types
def transaction():
    
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
        return render_template("transactions.html", username=username)

    # Checks for possible errors
    if not request.form.get("transaction"):
        flash("Must provide transaction type!")
        return render_template("transactions.html", username=username)

    elif not request.form.get("amount"):
        flash("Must provide the amount of money for transaction!")
        return render_template("transactions.html", username=username)

    elif int(request.form.get("amount")) <= 0: 
        flash("Must provide a positive integer")
        return render_template("transactions.html", username=username)
        
    elif not request.form.get("possession"):
        flash("Must provide type of possession!")
        return render_template("transactions.html", username=username)


    transaction_type = request.form.get("transaction")
    possession_type = request.form.get("possession")
    amount = int(request.form.get("amount"))

    # Validation is to check whether is there a similar entry or not with the given transaction type (old query for 2 databases)
    validation = cur.execute(   """
                                SELECT id
                                FROM transactions WHERE username = ?
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
        
        connection.commit()

    elif request.form.get("transaction") == "Withdraw":

        # New query for one database to get the amount for each possession type
        cash = cur.execute(     """
                                SELECT SUM(amount)
                                AS amount 
                                FROM transactions 
                                WHERE username = ? 
                                AND possession_type = ? 
                                AND transaction_type = ? 
                                """
                                , (username, possession_type, "Deposit",))

        cash_count = cash.fetchall()
        # If there is no entry yet inserts the given data
        if count == 0:
                flash("Amount can't be higher than asset amount")
                return render_template("transactions.html", username=username)

        # Checks if the user has enough assets and acts based on that   
        elif cash_count[0]["amount"] <= amount:
                flash("Amount can't be higher than asset amount")
                return render_template("transactions.html", username=username)
        elif cash_count[0]["amount"] >= amount:
        
            cur.execute(    """
                            INSERT INTO transactions (username, transaction_type, possession_type, amount) 
                            VALUES (?, ?, ?, ?)
                            """
                            , (username, transaction_type, possession_type, amount * (-1) ,))


        connection.commit()

    connection.close()
    return redirect("/")

@app.route("/reports")
@login_required
# This functions return the reports of all transactions made from an account
def reports():

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
    return render_template("reports.html", reports=reports, username=username)

@app.route("/budget")
@login_required
def budget():
    return render_template("budget.html")


@app.route("/admin")
@login_required
# This function returns a dashboard for the admin user
def admin():


    connection = sqlite3.connect("testDB.db")
    connection.row_factory = dict_factory
    cur = connection.cursor()



    if session["user_id"] == 1:

        users = cur.execute(    """
                                    SELECT
                                    username, id
                                    FROM
                                    users
                                    """)

        users_data = users.fetchall()

        user_data = cur.execute(    """
                                SELECT username
                                FROM users
                                WHERE id = ?
                                """
                                ,(session["user_id"],))

        # Returns current user's data needed for the report
        user = user_data.fetchall()
        username = user[0]["username"]

        connection.close()
        return render_template("admin.html", users_data=users_data, username=username)
        
    else:
        flash("You can only access this page with an admin profile!")
        return redirect("/")


@app.route("/delete", methods=["POST"])
@login_required
#This function lets a user with admin priviliges delete other users
def delete():

    connection = sqlite3.connect("testDB.db")
    connection.row_factory = dict_factory
    cur = connection.cursor()
    user_id = request.form.get("id")
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    connection.commit()
    connection.close()

    return redirect("/admin")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int("3000"), debug=True)