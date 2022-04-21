import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
# db = SQL("sqlite:///finance.db")
uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://")
db = SQL(uri)

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Get all the information about user's portfolio
    user_portfolio = db.execute("SELECT * FROM portfolio WHERE user_id = ?", session['user_id'])

    # Get user's owned stock symbols to lookup their current price
    user_stocks = db.execute("SELECT symbol FROM portfolio WHERE user_id = ?", session['user_id'])

    # Lookup current prices of stocks the user owns into a dictionary
    current_prices = {}
    for stock in user_stocks:
        current_prices[stock['symbol']] = lookup(stock['symbol'])['price']

    # Get the current cash user has
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session['user_id'])[0]['cash']
    total_balance = cash

    # Calculate total_balance by multiplying current price by the number of shares
    for stock in user_portfolio:
        total_balance += current_prices[stock['symbol']] * stock['shares']

    # Render index html with relevant information
    return render_template("index.html",
                           portfolio=user_portfolio,
                           prices=current_prices,
                           cash=cash,
                           balance=total_balance)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":

        # Get symbol from user input and store it
        symbol_name = request.form.get("symbol")

        # Get number of shares from user input via "name", if the input is not an integer return apolgy
        try:
            number_of_shares = int(request.form.get("shares"))
        except:
            return apology("Must provide valid number of shares!")

        # Ensure shares was submitted
        if not number_of_shares:
            return apology("Must provide share number!")

        # Ensure shares is positive number
        if number_of_shares < 1:
            return apology("Must provide valid number of shares!")

        # Ensure symbol name was submitted
        if not symbol_name:
            return apology("Must provide a stock symbol")

        # Look up stock data by using lookup function that uses the API_KEY
        stock_data = lookup(symbol_name)

        # Ensure stock ticker is correctly submitted
        if not stock_data:
            return apology("Stock not found!")

        # Get user's balance from database using user session id
        user_balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

        print(f"User balance: {user_balance}")
        print(f"User balance type: {type(user_balance)}")

        print(f"Shares: {number_of_shares}")
        print(f"Shares type: {type(number_of_shares)}")
        print(f"Price: {stock_data['price']}")
        print(f"Price type: {type(stock_data['price'])}")

        print(f"Company name: {stock_data['name']}")
        print(f"Date: {datetime.now()}")

        # Calculate the cost of purchase
        purchase = number_of_shares * stock_data["price"]

        # Get the current time to store purchase time
        date = datetime.now()
        print(f"Date iliu: {date.strftime('%c')}")

        print(f"Purchase: {purchase}")
        print(f"Purchase type: {type(purchase)}")

        # Ensure the user has enough cash to make the purchase
        if user_balance < purchase:
            return apology("You don't have enough capital to make this purchase")
        else:
            # Update cash to reflect purchased stock
            db.execute("UPDATE users SET cash = ? WHERE id = ?", user_balance - purchase, session["user_id"])

            # Add the stock purchase to user portfolio
            db.execute("INSERT INTO portfolio (user_id, company, symbol, shares, open, buy_date) VALUES(?, ?, ?, ?, ?, ?)",
                       session["user_id"],
                       stock_data["name"],
                       stock_data["symbol"],
                       number_of_shares,
                       stock_data["price"],
                       date.strftime('%c'))

            # Add to the transaction history
            db.execute("INSERT INTO transactions (user_id, company, SYMBOL, shares, type, price, date, 'profit-loss') VALUES(?, ?, ?, ?, ?, ?, ? ,?)",
                       session['user_id'],
                       stock_data["name"],
                       stock_data["symbol"],
                       number_of_shares,
                       "buy",
                       stock_data["price"],
                       date.strftime('%c'),
                       0)

            # Redirect user to home page
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Get user's transaction history
    user_transaction = db.execute("SELECT * FROM transactions WHERE user_id = ?", session['user_id'])
    print(f"Transaction: {user_transaction}")

    return render_template("history.html", transaction=user_transaction)


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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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

        # Get symbol from user input and store it
        symbol_name = request.form.get("symbol")

        # Ensure symbol name was submitted
        if not symbol_name:
            return apology("Must provide a stock symbol")

        # Look up stock data by using lookup function that uses the API_KEY
        stock_data = lookup(symbol_name)

        # Ensure stock ticker is correctly submitted
        if not stock_data:
            return apology("Stock not found!")

        # Redirect to quoted.html that displays the stock data
        return render_template("quoted.html", name=stock_data["name"], price=usd(stock_data["price"]), symbol=stock_data["symbol"])

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Fetch data from the form
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        usernames = db.execute("SELECT username FROM users")

        # Ensure username was submitted
        if not username:
            return apology("Must provide a username")

        # Ensure username is unique and not in the database
        for name in usernames:
            print(name['username'])
            if name['username'] == username:
                return apology("The username already exists, please try another username")

        # Ensure password was submitted
        if not password:
            return apology("Must provide a password")

        # Ensure confirmation was submitted
        if not confirmation:
            return apology("Must provide a confirmation", 400)

        # Ensure confirmation was submitted and match the password
        if password != confirmation:
            return apology("Password and confirmation must match")

        # Register the new user in the database
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, generate_password_hash(password))

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get symbol from user input and store it
        symbol = request.form.get("symbol")

        # Get number of shares user wants to sell
        how_many_shares = int(request.form.get("shares"))

        print(f"How many shares they want to sell: {how_many_shares}")
        print(f"Which stock they want to sell: {symbol}")

        # Ensure symbol name was submitted
        if not symbol:
            return apology("Must provide a stock symbol")

        # Ensure symbol shares was submitted
        if not how_many_shares:
            return apology("Must provide how many stocks to sell")

        # Get all the information about user's portfolio
        user_portfolio = db.execute("SELECT * FROM portfolio WHERE user_id = ?", session['user_id'])

        # Make sure user submits the stock that they own
        user_stocks = []
        for stock in user_portfolio:
            user_stocks.append(stock['symbol'])
        print(f"User stocks: {user_stocks}")
        if symbol not in user_stocks:
            return apology("You don't own this stock!")

        # Get all the relavant information from user's portfolio for the stock that they want to sell
        stock_to_sell = db.execute("SELECT * FROM portfolio WHERE user_id = ? AND symbol = ?", session['user_id'], symbol)
        print(stock_to_sell)
        symbol_shares_user_own = stock_to_sell[0]['shares']
        stock_current_price = lookup(symbol)['price']

        # Calculate profit/loss
        avsan_zardal = stock_to_sell[0]['open'] * how_many_shares
        zarsan_une = stock_current_price * how_many_shares
        profit = zarsan_une - avsan_zardal

        # Calculate remaining shares to update user portfolio
        remaining_shares = stock_to_sell[0]['shares'] - how_many_shares

        # Get user's current cash balance
        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", session['user_id'])[0]['cash']
        print(f"User cash: {user_cash}")
        print(f"User cash type: {type(user_cash)}")
        print(f"Remaining shares: {remaining_shares}")

        print(f"Avsan zardal: {avsan_zardal}")
        print(f"Zarsan une: {zarsan_une}")
        print(f"Profit/loss: {profit}")

        # Get the current time to store purchase time
        date = datetime.now()

        # Make transaction and reflect that transaction in user portfolio and cash
        if symbol_shares_user_own > how_many_shares:

            # Make transaction
            db.execute("INSERT INTO transactions (user_id, company, SYMBOL, shares, type, price, date, 'profit-loss') VALUES(?, ?, ?, ?, ?, ?, ? ,?)",
                       session['user_id'],
                       stock_to_sell[0]['company'],
                       stock_to_sell[0]['symbol'],
                       how_many_shares,
                       "sell",
                       stock_current_price,
                       date.strftime('%c'),
                       profit)

            # Update portfolio
            db.execute("UPDATE portfolio SET shares = ? WHERE user_id = ? AND symbol = ? AND shares = ?",
                       remaining_shares,
                       session['user_id'],
                       symbol,
                       symbol_shares_user_own)

            # Update user cash
            db.execute("UPDATE users SET cash = ? WHERE id = ?", user_cash + zarsan_une, session['user_id'])

        elif symbol_shares_user_own == how_many_shares:

            # Make transaction
            db.execute("INSERT INTO transactions (user_id, company, SYMBOL, shares, type, price, date, 'profit-loss') VALUES(?, ?, ?, ?, ?, ?, ? ,?)",
                       session['user_id'],
                       stock_to_sell[0]['company'],
                       stock_to_sell[0]['symbol'],
                       how_many_shares,
                       "sell",
                       stock_current_price,
                       date.strftime('%c'),
                       profit)

            # Delete row from portfolio
            db.execute("DELETE FROM portfolio WHERE user_id = ? AND symbol = ? AND shares = ?", session['user_id'],
                       symbol,
                       symbol_shares_user_own)

            # Update user cash
            db.execute("UPDATE users SET cash = ? WHERE id = ?", user_cash + zarsan_une, session['user_id'])

        else:
            return apology("You are trying to sell more shares than you own for this particular stock.")

        print(f"Which stock: {stock_to_sell}")
        print(f"Ene stock hed bga ve: {stock_to_sell[0]['shares']}")
        print(f"Same thing? {symbol_shares_user_own} = {stock_to_sell[0]['shares']}")
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Get all the information about user's portfolio
        user_portfolio = db.execute("SELECT * FROM portfolio WHERE user_id = ?", session['user_id'])

        return render_template("sell.html", portfolio=user_portfolio)