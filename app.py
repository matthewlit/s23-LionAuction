from flask import Flask, render_template, request, session, redirect
from flask_session import Session
import sqlite3 as sql
import bcrypt

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

host = 'http://127.0.0.1:5000/'


# Login Page
@app.route('/', methods=['GET', 'POST'])
def login():
    # On login button press
    if request.method == 'POST':
        roll = request.form['roll']
        username = request.form['username']
        password = request.form['password']

        # Gets hashed password from user database
        connection = sql.connect('database.db')
        if roll == 'bidder':
            cursor = connection.execute(
                'SELECT password FROM users,bidders WHERE users.email=? AND users.email=bidders.email',
                (username,))
        elif roll == 'seller':
            cursor = connection.execute(
                'SELECT password FROM users,sellers WHERE users.email=? AND users.email=sellers.email',
                (username,))
        elif roll == 'helpdesk':
            cursor = connection.execute(
                'SELECT password FROM users,helpdesk WHERE users.email=? AND users.email=helpdesk.email',
                (username,))
        result = cursor.fetchone()

        # Perform authentication check
        if result is not None and bcrypt.checkpw(password.encode('utf-8'), result[0]):
            # Redirect to new page based on roll
            session['username'] = username
            if roll == 'bidder':
                return redirect("/bidderMain")
            elif roll == 'seller':
                return redirect("/sellerMain")
            elif roll == 'helpdesk':
                return redirect("/helpdeskMain")
        else:
            return render_template('login.html', error='Invalid Login: Try Again')

    return render_template('login.html')


# Bidder Main Page
@app.route('/bidderMain', methods=['GET', 'POST'])
def bidderMain():
    # Get user info
    username = session.get('username')
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT first_name,last_name,email,age,gender,major,street_num,street_name,city,state,address.zipcode,credit_card_num '
        'FROM bidders,address,zipcode_info,credit_cards '
        'WHERE email=? '
        'AND bidders.home_address_id=address.address_ID '
        'AND address.zipcode=zipcode_info.zipcode '
        'AND bidders.email=credit_cards.Owner_email',
        (username,))
    userInfo = cursor.fetchone()

    # Create data list for page
    data = {"name": userInfo[0] + " " + userInfo[1],
            "email": userInfo[2],
            "roll": "Bidder",
            "age": userInfo[3],
            "gender": userInfo[4],
            "major": userInfo[5].title(),
            "address": str(userInfo[6]) + " " + userInfo[7] + ", " + userInfo[8] + ", " + userInfo[9] + " " + str(
                userInfo[10]),
            "card": "**** **** **** " + userInfo[11][-4:],
            "listings": getAuctionListings('Root'),
            "category": 'All',
            "categories": getCategories()}

    # On button press
    if request.method == 'POST':
        # Get category
        category = request.form['category']
        listings = getAuctionListings(category)
        data['listings'] = listings
        if category == 'Root': category = 'All'
        data["category"] = category
        return render_template('bidderMain.html', data=data)

    return render_template('bidderMain.html', data=data)


# Seller Main Page
@app.route('/sellerMain', methods=['GET', 'POST'])
def sellerMain():
    return render_template('sellerMain.html')


# Help Desk Main Page
@app.route('/helpdeskMain', methods=['GET', 'POST'])
def helpdeskMain():
    return render_template('helpdeskMain.html')


# Gets auction_listings in given category and subcategories
def getAuctionListings(category):
    listings = []

    # Get parent category
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT category_name FROM categories WHERE parent_category=?', (category,))
    categories = cursor.fetchall()

    # Add listings in parent category
    cursor = connection.execute('SELECT * FROM auction_listings WHERE Category=?', (category,))
    listing = cursor.fetchall()
    if listing: listings.append(listing)

    # Get subcategories
    for row in categories:
        cursor = connection.execute('SELECT category_name FROM categories WHERE parent_category=?', (row[0],))
        subcategory = cursor.fetchall()
        if subcategory:
            for cat in subcategory:
                categories.append(cat)

        # Add listings in category
        cursor = connection.execute('SELECT * FROM auction_listings WHERE Category=?', (row[0],))
        listing = cursor.fetchall()
        if listing: listings.append(listing)

    return listings


# Gets all categories in database
def getCategories():
    categories = []

    # Get categories
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT category_name FROM categories')
    categoryRows = cursor.fetchall()
    for row in categoryRows:
        categories.append(row[0])

    return categories


if __name__ == "__main__":
    app.run(debug=True)
