import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

import datetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    rows = db.execute("SELECT symbol, name, shares FROM users_tot WHERE id = :id", id=session["user_id"])
    if len(rows) > 0:
        price = []
        summ = []
        summ_r = 0

        for i in range(len(rows)):
            price.append(usd(lookup(rows[i]["symbol"])["price"]))
            summ.append(usd(lookup(rows[i]["symbol"])["price"] * rows[i]["shares"]))
            summ_r = summ_r + lookup(rows[i]["symbol"])["price"] * rows[i]["shares"]

        balance = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])[0]["cash"]
        total = balance + summ_r

        return render_template("index.html", rows = rows, price = price, summ = summ, ln = range(len(rows)), balance = usd(balance), total = usd(total))

    else:
        balance = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])[0]["cash"]
        total = balance
        return render_template("index2.html", balance = usd(balance), total = usd(total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        if not lookup(request.form.get("buy")):
            return apology("wrong symbol", 403)

        b_resp = lookup(request.form.get("buy"))
        summ = float(request.form.get("shares")) * b_resp["price"]
        balance1 = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])
        balance = balance1[0]["cash"] - summ

        if balance < 0:
            return apology("not enough money to make a purchase", 403)

        # Insert new transaction in users
        db.execute("UPDATE users SET cash = :balance WHERE id = :id", balance = balance, id=session["user_id"])

        # Query database for username and symbol
        rows = db.execute("SELECT * FROM users_tot WHERE symbol =:symb AND id = :id", symb = b_resp["symbol"], id=session["user_id"])

        # Insert new transaction in users_tot
        if len(rows) == 0:
            db.execute("INSERT INTO users_tot (id, symbol, name, shares) VALUES(?, ?, ?, ?)", session["user_id"],
                       b_resp["symbol"], b_resp["name"], int(request.form.get("shares")))

        else:
            sh1 = db.execute("SELECT shares FROM users_tot WHERE id =:id", id=session["user_id"])
            db.execute("UPDATE users_tot SET shares = :sh WHERE symbol =:symb AND id =:id",
                       sh = sh1[0]["shares"] + int(request.form.get("shares")), symb = b_resp["symbol"], id=session["user_id"])

        # Insert new transaction in users_inf
        db.execute("INSERT INTO users_inf (id, symbol, name, shares, price, transacted) VALUES(?, ?, ?, ?, ?, ?)", session["user_id"],
                   b_resp["symbol"], b_resp["name"], int(request.form.get("shares")), usd(b_resp["price"]), datetime.datetime.now());

        flash('Bought!')

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    rows = db.execute("SELECT symbol, shares, price, transacted FROM users_inf WHERE id =:id", id=session["user_id"])

    return render_template("history.html", rows = rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        flash('Logged in successfully!')

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        q_resp = lookup(request.form.get("quote"))

        if not lookup(request.form.get("quote")):
            return apology("wrong symbol", 403)

        else:
            return render_template("quote2.html", name = q_resp["name"], symbol = q_resp["symbol"], price = usd(q_resp["price"]))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote1.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username yet does not exist
        if len(rows) != 0:
            return apology("username is already taken", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure password(again) was submitted
        elif not request.form.get("password_again"):
            return apology("must provide password(again)", 403)

        # Ensure the re-entered password is the same
        elif request.form.get("password") != request.form.get("password_again"):
            return apology("passwords didn't match", 403)

        # Generate hash password
        hash = generate_password_hash(request.form.get("password"))

        # Insert new user in users
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", request.form.get("username"), hash)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        flash('Registred!')

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    rows = db.execute("SELECT symbol FROM users_tot WHERE id = :id", id=session["user_id"])

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        s_resp = lookup(request.form.get("sell"));
        summ = float(request.form.get("shares")) * s_resp["price"];
        balance = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])[0]["cash"] + summ;

        if int(request.form.get("shares")) > db.execute("SELECT shares FROM users_tot WHERE symbol = :symbol AND id = :id",
                symbol=request.form.get("sell"), id=session["user_id"])[0]["shares"]:
            return apology("not enough shares to sell", 403)

        else:
            # Insert new transaction in users
            db.execute("UPDATE users SET cash = :balance WHERE id = :id", balance = balance, id=session["user_id"]);

            # Insert new transaction in users_tot
            sh1 = db.execute("SELECT shares FROM users_tot WHERE symbol = :symbol AND id =:id", symbol=request.form.get("sell"), id=session["user_id"])
            db.execute("UPDATE users_tot SET shares = :sh WHERE symbol =:symb AND id = :id",
                       sh = sh1[0]["shares"] - int(request.form.get("shares")),  symb = s_resp["symbol"], id=session["user_id"])

            # Delete row if number of shares equal 0
            db.execute("DELETE FROM users_tot WHERE shares = 0 AND id =:id", id=session["user_id"])

            # Insert new transaction in users_inf
            db.execute("INSERT INTO users_inf (id, symbol, name, shares, price, transacted) VALUES(?, ?, ?, ?, ?, ?)", session["user_id"],
                        s_resp["symbol"], s_resp["name"], '-' + request.form.get("shares"), usd(s_resp["price"]), datetime.datetime.now());

            flash('Sold!')

            return redirect("/")


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("sell.html", rows = rows)


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change password"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure old password was submitted
        elif not request.form.get("old_password"):
            return apology("must provide old password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and old password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("old_password")):
            return apology("invalid username and/or old password", 403)

        # Ensure new password was submitted
        elif not request.form.get("new_password"):
            return apology("must provide new password", 403)

        # Ensure new password (again) was submitted
        elif not request.form.get("new_password_again"):
            return apology("must provide new password (again)", 403)

        # Ensure the re-entered new password is the same
        elif request.form.get("new_password") != request.form.get("new_password_again"):
            return apology("new passwords didn't match", 403)

        # Generate hash password
        hash = generate_password_hash(request.form.get("new_password"))

        db.execute("UPDATE users SET hash = :hash WHERE id = :id", hash = hash, id=session["user_id"])

        flash('Changed!')

        return redirect("/")

    else:
        return render_template("change_password.html")



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
