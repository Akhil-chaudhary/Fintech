import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

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



# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///fintech.db")


@app.route("/", methods=["GET", "POST"])
#@login_required
def index():
    if request.method == "GET":
        return render_template("index.html")





@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("email"):
            error = "Please provide Email account"
            return render_template("login.html", error = error)

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = "Please provide a Password"
            return render_template("login.html", error = error)
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = :mail;", mail=request.form.get("email"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            error = "Email/Password Invalid"
            return render_template("login.html", error = error)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "POST":
        mail = request.form.get("email")
        password = request.form.get("password")

        if not mail or not password:
            error = "Please provide a Username and Password"
            return render_template("register.html", error = error)

        test = request.form.get("confirmation")
        if password != test:
            error = "Passwords did not match"
            return render_template("register.html", error = error)

        phash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        result = db.execute("Select * from users where email = :email;", email = mail)

        if result != [] :
            error = "Provided Email is used in another account"
            return render_template("register.html", error = error)

        db.execute("Insert into users(email,password) values(:mail,:hash);", mail = request.form.get("email"), hash = phash)
        row = db.execute("Select user_id from users where email = :mail;", mail = mail)
        session["user_id"] = row[0]["user_id"]

        #db.execute("Insert into portfolio(user_id) values(:i)", i = row[0])
        return redirect("/")

    else:
        return render_template("register.html")