"""
Author: Matthew Kelleher
Last Modified: April 24, 2023
"""

from flask import Flask, render_template, request, session, redirect
from flask_session import Session
import sqlite3 as sql
import bcrypt
import datetime

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

host = 'http://127.0.0.1:5000/'


# <----------------------------------------- Page Functions ----------------------------------------->

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
        cursor = None
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
        'SELECT bank_routing_number, bank_account_number, balance FROM sellers WHERE email=?', (username,))
    userInfo = cursor.fetchone()

    # Create data list for page
    data = {"email": username,
            "roll": "Seller",
            "bank_routing_number": userInfo[0],
            "bank_account_number": userInfo[1],
            "balance": userInfo[2],
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
        data['business_address'] = str(vendor[1]) + " " + vendor[2] + ", " + vendor[3] + ", " + vendor[4] + " " + str(
            vendor[5])
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
        # Get category
        if request.form['button'] == 'Submit':
            category = request.form['category']
            listings = getAuctionListings(category)
            data['listings'] = listings
            if category == 'Root':
                category = 'All'
            data['category'] = category
            return render_template('auctionListings.html', data=data)

        # Redirect to page to bid and get more info
        else:
            session['listing_ID'] = request.form['button']
            return redirect("/bid")

    return render_template('auctionListings.html', data=data)


# Bid Status Page
@app.route('/bidStatus', methods=['GET', 'POST'])
def bidStatusPage():
    username = session.get('username')

    data = {"username": username,
            "listings": getBids(username)
            }

    if request.method == 'POST':
        # Redirect to page to bid and get more info
        session['listing_ID'] = request.form['button']
        return redirect("/bid")

    return render_template('bidStatus.html', data=data)


# Bidding Page
@app.route('/bid', methods=['GET', 'POST'])
def bidPage():
    listing_ID = session.get('listing_ID')
    username = session.get('username')

    data = {"username": username,
            "info": getAuctionInfo(listing_ID)
            }

    # Add minimum bid amount
    if data['info'][12] != 'No Bids':
        data['minimumBid'] = (data['info'][12]) + 1
    else:
        data['minimumBid'] = (data['info'][7])

    # On bid button press
    if request.method == 'POST':
        bidAmount = int(request.form['bidAmount'])
        if bidAmount >= data['minimumBid']:
            # Place bid
            placeBid(username, listing_ID, bidAmount)

            # Update data
            data = {"username": username, "info": getAuctionInfo(listing_ID), 'minimumBid': bidAmount + 1}

            return render_template('bid.html', data=data, error='Placed $' + str(bidAmount) + ' bid')
        else:
            return render_template('bid.html', data=data, error='Invalid Amount')

    return render_template('bid.html', data=data)


# Seller Auction Status Page
@app.route('/auctionStatus', methods=['GET', 'POST'])
def auctionStatusPage():
    username = session.get('username')

    # Create data list for page
    data = {"listings": getSellerAuctions(username),
            "categories": getAllCategories()
            }

    # On button press
    if request.method == 'POST':
        # Create new auction
        if 'confirm_add_button' in request.form:
            Seller_Email = username
            Category = request.form['category']
            Auction_Title = request.form['Auction_Title']
            Product_Name = request.form['Product_Name']
            Product_Description = request.form['Product_Description']
            Quantity = request.form['Quantity']
            Reserve_Price = request.form['Reserve_Price']
            Max_bids = request.form['Max_Bid']
            newAuction(Seller_Email, Category, Auction_Title, Product_Name, Product_Description, Quantity,
                       Reserve_Price, Max_bids)

        # Set auction as active
        elif 'confirm_activate_button' in request.form:
            Listing_ID = request.form['confirm_activate_button']
            setActive(Listing_ID)

        # Set auction as inactive
        elif 'confirm_deactivate_button' in request.form:
            Listing_ID = request.form['confirm_deactivate_button']
            Reason = request.form['Reason']
            setInactive(Listing_ID, Reason)

        # Edit auction
        elif 'confirm_edit_button' in request.form:
            Listing_ID = request.form['confirm_edit_button']
            Category = request.form['category']
            Auction_Title = request.form['Auction_Title']
            Product_Name = request.form['Product_Name']
            Product_Description = request.form['Product_Description']
            Quantity = request.form['Quantity']
            Reserve_Price = request.form['Reserve_Price']
            Max_bids = request.form['Max_Bid']
            editAuction(Listing_ID, Category, Auction_Title, Product_Name, Product_Description, Quantity, Reserve_Price,
                        Max_bids)

        # Complete Transaction:
        elif 'confirm_complete_button' in request.form:
            Listing_ID = request.form['confirm_complete_button']
            completeTransaction(Listing_ID)

        # Update page
        data['listings'] = getSellerAuctions(username)
        return render_template('auctionStatus.html', data=data)

    return render_template('auctionStatus.html', data=data)


# <----------------------------------------- Helper Functions ----------------------------------------->


# Gets auction listings in given category and subcategories
def getAuctionListings(category):
    listings = []

    # Get parent category
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT category_name FROM categories WHERE parent_category=?', (category,))
    categories = cursor.fetchall()

    # Add listings in parent category
    cursor = connection.execute('SELECT Listing_ID FROM auction_listings WHERE Category=? AND Status=1', (category,))
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
        cursor = connection.execute('SELECT Listing_ID FROM auction_listings WHERE Category=? AND Status=1', (row[0],))
        listing = cursor.fetchall()
        if listing:
            for auction in listing:
                listings.append(getAuctionInfo(auction[0]))

    return listings


# Gets all sellers posted auctions
def getSellerAuctions(user):
    listings = []

    # Get auctions
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT Listing_ID FROM auction_listings WHERE Seller_Email=? ORDER BY Status', (user,))
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
        for b in bids:
            bidsList.append(getAuctionInfo(b[0]))
    return bidsList


# Gets all information of a given auction
def getAuctionInfo(Listing_ID):
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
    if info2 is None:
        info2 = ('No Bids',)
    # Gets highest bid in auction
    cursor = connection.execute('SELECT max(Bid_price) FROM bids '
                                'WHERE Listing_ID = ? GROUP BY Listing_ID', (Listing_ID,))
    info3 = cursor.fetchone()
    if info3 is None:
        info3 = ('No Bids',)

    # Get remaining bids
    cursor = connection.execute('SELECT count(Bid_ID) FROM bids '
                                'WHERE Listing_ID = ?', (Listing_ID,))
    numBids = cursor.fetchone()
    info4 = (info1[8] - numBids[0],)

    # If winner
    info5 = ('No winner',)
    if info1[9] == 2:
        # Get winner
        cursor = connection.execute('SELECT Bidder_email,max(Bid_price) FROM bids '
                                    'WHERE Listing_ID = ? GROUP BY Listing_ID', (Listing_ID,))
        winner = cursor.fetchone()[0]

        # Get if transaction complete
        complete = 0
        cursor = connection.execute('SELECT * FROM transactions WHERE Listing_ID = ?', (Listing_ID,))
        if cursor.fetchone():
            complete = 1
        info5 = (winner, complete)

    auctionInfo = info1 + info2 + info3 + info4 + info5

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
        cursor = connection.execute('SELECT * FROM auction_listings WHERE Category=? AND Status=1', (row[0],))
        if cursor.fetchone():
            categories.append(row[0])

    return categories


# Gets all categories in database
def getAllCategories():
    categories = []

    # Get categories
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT category_name FROM categories')
    categoryRows = cursor.fetchall()
    for row in categoryRows:
        categories.append(row[0])

    return categories


# Set auction as active
def setActive(Listing_ID):
    # Set as active
    connection = sql.connect('database.db')
    connection.execute('UPDATE auction_listings SET Status=?, Remove_Reason=? WHERE Listing_ID=?', (1, "", Listing_ID,))
    connection.commit()
    return


# Set auction as inactive
def setInactive(Listing_ID, reason):
    # Set as inactive
    connection = sql.connect('database.db')
    connection.execute('UPDATE auction_listings SET Status=?, Remove_Reason=? WHERE Listing_ID=?',
                       (0, reason, Listing_ID))
    connection.commit()
    return


# Create new auction
def newAuction(Seller_Email, Category, Auction_Title, Product_Name, Product_Description, Quantity, Reserve_Price,
               Max_bids):
    # Create new Listing_ID
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT max(Listing_ID) FROM auction_listings')
    maxListingID = cursor.fetchone()[0]
    newListingID = maxListingID + 1

    # Add to auction listings
    connection.execute('INSERT INTO auction_listings '
                       '(Seller_Email, Listing_ID, Category, Auction_Title, Product_Name, Product_Description, '
                       'Quantity, Reserve_Price, Max_bids, Status, Remove_Reason) '
                       'VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                       (Seller_Email, newListingID, Category, Auction_Title, Product_Name,
                        Product_Description, Quantity, Reserve_Price, Max_bids, 1, ""))
    connection.commit()
    return


# Edit an existing auction
def editAuction(Listing_ID, Category, Auction_Title, Product_Name, Product_Description, Quantity, Reserve_Price,
                Max_bids):
    # Update listing
    connection = sql.connect('database.db')
    connection.execute('UPDATE auction_listings SET '
                       '(Category, Auction_Title, Product_Name, Product_Description, '
                       'Quantity, Reserve_Price, Max_bids) = (?,?,?,?,?,?,?) WHERE Listing_ID=?',
                       (Category, Auction_Title, Product_Name, Product_Description, Quantity, Reserve_Price, Max_bids,
                        Listing_ID))
    connection.commit()
    return


# Place a new bid
def placeBid(user, Listing_ID, bidAmount):
    # Get auction info
    info = getAuctionInfo(Listing_ID)

    # Create new Bid_ID
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT max(Bid_ID) FROM bids')
    maxBidID = cursor.fetchone()[0]
    Bid_ID = maxBidID + 1

    # Add to bid table
    connection.execute('INSERT INTO bids (Bid_ID, Seller_Email, Listing_ID, Bidder_email, Bid_price) '
                       'VALUES (?,?,?,?,?)', (Bid_ID, info[0], Listing_ID, user, bidAmount))
    connection.commit()

    # Checks if bid is over
    if info[13] == 1:
        # Set as sold
        connection.execute('UPDATE auction_listings SET Status=?, Remove_Reason=? WHERE Listing_ID=?',
                           (2, "", Listing_ID,))
        connection.commit()

    return


# Complete transaction
def completeTransaction(Listing_ID):
    # Get auction info
    info = getAuctionInfo(Listing_ID)

    # Create new Transaction_ID
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT max(Bid_ID) FROM bids')
    maxTransactionID = cursor.fetchone()[0]
    Transaction_ID = maxTransactionID + 1

    # Get date
    current_time = datetime.datetime.now()
    date = str(current_time.month) + "/" + str(current_time.day) + "/" + str(current_time.year)

    # Insert into transactions table
    connection.execute(
        'INSERT INTO transactions (Transaction_ID, Seller_Email, Listing_ID, Buyer_Email, Date, Payment) '
        'VALUES (?,?,?,?,?,?)', (Transaction_ID, info[0], Listing_ID, info[14], date, info[12]))
    connection.commit()

    # ***Charge bidder credit card***

    # Add Payment to sellers balance
    cursor = connection.execute('SELECT balance FROM sellers WHERE email=?', (info[0],))
    balance = (cursor.fetchone()[0]) + info[12]
    connection.execute('UPDATE sellers SET balance=? WHERE email=?',
                       (balance, info[0],))
    connection.commit()

    return


if __name__ == "__main__":
    app.run(debug=True)
