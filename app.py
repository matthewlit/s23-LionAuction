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
def loginPage():
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
def bidderMainPage():
    # Get user info
    username = session.get('username')
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT first_name,last_name,age,gender,major,street_num,street_name,city,state,address.zipcode,credit_card_num '
        'FROM bidders,address,zipcode_info,credit_cards '
        'WHERE email=? '
        'AND bidders.home_address_id=address.address_ID '
        'AND address.zipcode=zipcode_info.zipcode '
        'AND bidders.email=credit_cards.Owner_email',
        (username,))
    userInfo = cursor.fetchone()

    # Create data list for page
    data = {"name": userInfo[0] + " " + userInfo[1],
            "email": username,
            "roll": "Bidder",
            "age": userInfo[2],
            "gender": userInfo[3],
            "major": userInfo[4].title(),
            "address": str(userInfo[5]) + " " + userInfo[6] + ", " + userInfo[7] + ", " + userInfo[8] + " " + str(
                userInfo[9]),
            "card": "**** **** **** " + userInfo[10][-4:]
            }

    return render_template('bidderMain.html', data=data)


# Seller Main Page
@app.route('/sellerMain', methods=['GET', 'POST'])
def sellerMainPage():
    # Get user info
    username = session.get('username')
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT bank_routing_number, bank_account_number FROM sellers WHERE email=?', (username,))
    userInfo = cursor.fetchone()

    # Create data list for page
    data = {"email": username,
            "roll": "Seller",
            "bank_routing_number": userInfo[0],
            "bank_account_number": userInfo[1],
            "business_name": None,
            "business_address": None,
            "customer_service": None
            }

    # If local vendor add info
    cursor = connection.execute(
        'SELECT Business_Name,street_num,street_name,city,state,address.zipcode,Customer_Service_Phone_Number '
        'FROM local_vendors,address,zipcode_info '
        'WHERE email=? '
        'AND local_vendors.Business_Address_ID=address.address_ID '
        'AND address.zipcode=zipcode_info.zipcode', (username,))
    vendor = cursor.fetchone()
    if vendor:
        data['business_name'] = vendor[0]
        data['business_address'] = str(vendor[1]) + " " + vendor[2] + ", " + vendor[3] + ", " + vendor[4] + " " + str(vendor[5])
        data['customer_service'] = vendor[6]

    return render_template('sellerMain.html', data=data)


# Help Desk Main Page
@app.route('/helpdeskMain', methods=['GET', 'POST'])
def helpdeskMainPage():
    # Get user info
    username = session.get('username')
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT position FROM helpdesk WHERE email=?', (username,))
    userInfo = cursor.fetchone()

    # Create data list for page
    data = {"email": username,
            "roll": "Help Desk",
            "position": userInfo[0]
            }

    return render_template('helpdeskMain.html', data=data)


# Auction Listing Page
@app.route('/auctionListings', methods=['GET', 'POST'])
def auctionListingsPage():
    # Create data list for page
    data = {"listings": getAuctionListings('Root'),
            "category": 'All',
            "categories": getCategories()
            }

    # On button press
    if request.method == 'POST':
        if request.form['button'] == 'Submit':
            # Get category
            category = request.form['category']
            listings = getAuctionListings(category)
            data['listings'] = listings
            if category == 'Root': category = 'All'
            data['category'] = category
            return render_template('auctionListings.html', data=data)

        else:
            # Redirect to page to bid and get more info
            session['listing_ID'] = request.form['button']
            return redirect("/bid")

    return render_template('auctionListings.html', data=data)


# Bid Status Page
@app.route('/bidStatus', methods=['GET', 'POST'])
def bidStatusPage():
    username = session.get('username')

    if request.method == 'POST':
        # Redirect to page to bid and get more info
        session['listing_ID'] = request.form['bid_button']
        return redirect("/bid")

    return render_template('bidStatus.html', data=getBids(username))


# Bidding Page
@app.route('/bid', methods=['GET', 'POST'])
def bidPage():
    listing_ID = session.get('listing_ID')

    return render_template('bid.html', data=getAuctionInfo(listing_ID))


# Gets auction_listings in given category and subcategories
def getAuctionListings(category):
    listings = []

    # Get parent category
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT category_name FROM categories WHERE parent_category=?', (category,))
    categories = cursor.fetchall()

    # Add listings in parent category
    cursor = connection.execute('SELECT Listing_ID FROM auction_listings WHERE Category=?', (category,))
    listing = cursor.fetchall()
    if listing:
        for auction in listing:
            listings.append(getAuctionInfo(auction[0]))

    # Get subcategories
    for row in categories:
        cursor = connection.execute('SELECT category_name FROM categories WHERE parent_category=?', (row[0],))
        subcategory = cursor.fetchall()
        if subcategory:
            for cat in subcategory:
                categories.append(cat)

        # Add listings in category
        cursor = connection.execute('SELECT Listing_ID FROM auction_listings WHERE Category=?', (row[0],))
        listing = cursor.fetchall()
        if listing:
            for auction in listing:
                listings.append(getAuctionInfo(auction[0]))

    return listings


# Gets auctions the user had bids on
def getBids(user):
    bidsList = []

    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT auction_listings.Listing_ID,max(Bid_price) FROM auction_listings,bids '
                                'WHERE auction_listings.Listing_ID = bids.Listing_ID '
                                'AND bids.Bidder_email=? GROUP BY bids.Listing_ID', (user,))
    bids = cursor.fetchall()
    if bids:
        for bid in bids:
            bidsList.append(getAuctionInfo(bid[0]))
    return bidsList


# Gets all information of a given auction
def getAuctionInfo(Listing_ID):
    auctionInfo = ()

    connection = sql.connect('database.db')
    # Gets auction details
    cursor = connection.execute('SELECT auction_listings.* FROM auction_listings '
                                'WHERE Listing_ID=?', (Listing_ID,))
    info1 = cursor.fetchone()
    # Gets users highest bid
    cursor = connection.execute('SELECT max(Bid_price) FROM bids '
                                'WHERE Listing_ID = ? AND Bidder_email=? GROUP BY Listing_ID',
                                (Listing_ID, session.get('username'),))
    info2 = cursor.fetchone()
    if info2 is None: info2 = ('No Bids',)
    # Gets highest bid in auction
    cursor = connection.execute('SELECT max(Bid_price) FROM bids '
                                'WHERE Listing_ID = ? GROUP BY Listing_ID', (Listing_ID,))
    info3 = cursor.fetchone()
    if info3 is None: info3 = ('No Bids',)

    auctionInfo = info1 + info2 + info3

    return auctionInfo


# Gets all categories in database with listings
def getCategories():
    categories = []

    # Get categories
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT category_name FROM categories')
    categoryRows = cursor.fetchall()
    for row in categoryRows:
        # Check if category has listings
        cursor = connection.execute('SELECT * FROM auction_listings WHERE Category=?', (row[0],))
        if cursor.fetchone():
            categories.append(row[0])

    return categories


if __name__ == "__main__":
    app.run(debug=True)
