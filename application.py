import os
import requests
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
#from helpers import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
#session["global_id"] = None
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
a=False

@app.route("/", methods=["GET", "POST"])
def index():
    resNews = requests.get("https://newsapi.org/v2/everything?q=finance&from=2019-10-15&to=2019-10-15&sortBy=popularity&apiKey=16c14d73a1a24a76a5145fcda13637df")
    data = resNews.json()
    news = []
    for i in range(6):
        if data["status"] == "ok":
            dict={}
            dict["title"] = data["articles"][i]["title"],
            dict["description"] = data["articles"][i]["title"],
            dict["url"] = data["articles"][i]["url"],
            dict["urlToImage"] = data["articles"][i]["urlToImage"],
            dict["publishedAt"]= data["articles"][i]["publishedAt"]
        news.append(dict)
    if request.method == "GET":
        if session.get("user_id") is None:
            return render_template("index.html",key = "Logi",news= news)
        else:
            userName = db.execute("select name from users where user_id=:i_d",i_d = session.get("user_id"))
            key = userName[0]["name"]
            return render_template("index.html",key=key,news=news)

    else:
        userlog = db.execute("SELECT is_logged FROM users WHERE user_id=:i_d;", i_d=session["user_id"])
        if userlog == 0:
            return render_template("index.html",key="Login",news=news)

        elif userlog == 1:
            username = "Dev"
            return render_template("index.html",key = username,news=news)



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
        a=True
        #CHange the bool is_logged
        i_d = session["user_id"]
        db.execute(f"UPDATE users SET is_logged = 1 WHERE user_id = {i_d};")

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
        name = request.form.get("name")
        mail = request.form.get("email")
        password = request.form.get("password")

        if not mail or not password or not name:
            error = "Please provide a Name, Email and Password"
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

        db.execute("Insert into users(email,password,is_logged,name) values(:mail,:hash,:booled,:name);", mail = request.form.get("email"), hash = phash, booled = 0,name=name)
        row = db.execute("Select user_id from users where email = :mail;", mail = mail)
        session["user_id"] = row[0]["user_id"]
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/currency", methods=["GET", "POST"])
def currency():
    """Currency converteer"""
    if request.method == "GET":
        return render_template("currency.html", calculated = "click Convert")
    elif request.method == "POST":
        amt = request.form.get("amount")
        base = request.form.get("currency1")
        symbol = request.form.get("currency2")
        res = requests.get(f"http://data.fixer.io/api/latest?access_key=87234300c621de72126485e18b505d08&symbols={base},{symbol}&format=1")
        data = res.json()
        changed = (data['rates']['USD'] /data['rates']['INR']) * amt
        info = changed + symbol
        return render_template("currencyChanged.html", calculated=info)


@app.route("/exp", methods=["GET","POST"])
def exp():
    return render_template("exp.html")



@app.route("/loan", methods=["GET","POST"])
def loan():
    return render_template("loan.html")



@app.route("/tax", methods=["GET","POST"])
def tax():
    return render_template("taxcal.html")