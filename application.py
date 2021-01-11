from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, usd

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
db = SQL("sqlite:///trip.db")



@app.route("/", methods=["GET", "POST"])
def index():
    """Main"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Insert new wish in wishes
        if request.form.get("wishes"):

            db.execute("INSERT INTO wishes (name, wish) VALUES(?, ?)", request.form.get("name"), request.form.get("wishes"));

            flash('Sent wishes!')

        if request.form.get("reviews"):

            db.execute("INSERT INTO reviews (name, review) VALUES(?, ?)", request.form.get("name1"), request.form.get("reviews"));

            flash('Sent reviews!')

        # Redirect user to main page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("index.html")



@app.route("/my_page", methods=["GET", "POST"])
@login_required
def my_page():
    """Show My Page"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Insert new wish in wishes
        if request.form.get("wishes"):
            db.execute("INSERT INTO wishes (name, wish) VALUES(?, ?)", request.form.get("name"), request.form.get("wishes"));
            flash('Sent wishes!')
            # Redirect user to my page
            return redirect("/my_page")

        if request.form.get("reviews"):
            db.execute("INSERT INTO reviews (name, review) VALUES(?, ?)", request.form.get("name1"), request.form.get("reviews"));
            flash('Sent reviews!')
            # Redirect user to my page
            return redirect("/my_page")

        if request.form['index']:
            index = request.form['index']
            rows1 = db.execute("SELECT * FROM trip_price WHERE trip = :index", index = index)
            db.execute("INSERT INTO temp (trip) VALUES(?)", index);
            rows2 = db.execute("SELECT * FROM duration")
            rows3 = db.execute("SELECT * FROM return")
            return render_template("buy.html", tr = rows1[0]["trip"], pr = usd(rows1[0]["price"]), rows2 = rows2, rows3 = rows3)

        else:
            return redirect("/my_page")


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("my_page.html")




@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy trip"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        rows0 = db.execute("SELECT * FROM temp")
        ln = len(rows0)
        t = rows0[ln - 1]["trip"]
        rows1 = db.execute("SELECT * FROM trip_price WHERE trip = :trip", trip = t)
        db.execute("DELETE FROM temp WHERE trip = :trip", trip = t)
        summ = int(request.form.get("persons")) * rows1[0]["price"]
        balance1 = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])
        balance = balance1[0]["cash"] - summ

        if balance < 0:
            return apology("not enough money to make a purchase")

        # Insert new purchase in users_trip
        db.execute("INSERT INTO users_trip (id, trip, persons, total_price, duration, return) VALUES(?, ?, ?, ?, ?, ?)", session["user_id"],
                   rows1[0]["trip"], int(request.form.get("persons")), summ, request.form.get("duration"), request.form.get("return"));

        # Update cash in users
        db.execute("UPDATE users SET cash = :balance WHERE id = :id", balance = balance, id=session["user_id"])

        flash('Bought!')

        # Redirect user to home page
        return redirect("/my_page")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")



@app.route("/money", methods=["GET", "POST"])
@login_required
def money():
    """My Money"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Update cash in users
        summ = float(request.form.get("money"))
        balance1 = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])
        balance = balance1[0]["cash"] + summ

        db.execute("UPDATE users SET cash = :balance WHERE id = :id", balance = balance, id=session["user_id"])

        flash('Money is deposited into the account!')

        # Redirect user to home page
        return redirect("/my_page")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("money.html")


@app.route("/purchases")
@login_required
def purchases():
    """Show my purchases"""
    balance1 = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])
    balance = usd(balance1[0]["cash"])
    rows = db.execute("SELECT trip, persons, total_price, duration, return FROM users_trip WHERE id = :id", id=session["user_id"])
    price = []
    for i in range(len(rows)):
        price.append(usd(rows[i]["total_price"]))

    return render_template("purchases.html", ln = range(len(rows)), rows = rows, price = price, balance = balance)



@app.route("/comments")
def comments():
    """Show comments"""
    rows = db.execute("SELECT * FROM reviews")

    return render_template("comments.html", ln = range(len(rows)), rows = rows)



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

        # Redirect user to home page
        return redirect("/my_page")

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




@app.route("/cancel", methods=["GET", "POST"])
@login_required
def cancel():
    """Cancel Trip"""
    rows1 = db.execute("SELECT trip, persons FROM users_trip WHERE id = :id", id=session["user_id"])

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        rows2 = db.execute("SELECT persons FROM users_trip WHERE trip = :trip AND id = :id", trip=request.form.get("trip"), id=session["user_id"])
        new_persons = rows2[0]["persons"] - int(request.form.get("persons"))

        if new_persons < 0:
            return apology("not enough persons to sell", 403)

        price1 = db.execute("SELECT price FROM trip_price WHERE trip =:trip", trip = request.form.get("trip"))

        price2 = price1[0]["price"] * new_persons

        # Update users_trip
        db.execute("UPDATE users_trip SET persons = :persons, total_price = :total_price WHERE trip =:trip AND id = :id",
                       persons = new_persons, total_price = price2, trip = request.form.get("trip"), id=session["user_id"])

        # Delete row if number of persons equal 0
        db.execute("DELETE FROM users_trip WHERE persons = 0 AND id =:id", id=session["user_id"])

        new_balance = db.execute("SELECT cash FROM users WHERE id = :id",
                id=session["user_id"])[0]["cash"] + int(request.form.get("persons")) * price1[0]["price"]

        # Update users
        db.execute("UPDATE users SET cash = :cash WHERE id = :id", cash = new_balance, id=session["user_id"])

        flash('Cancel!')

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("cancel.html", rows1 = rows1)




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
