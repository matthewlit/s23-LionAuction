import sqlite3 as sql
import bcrypt
import csv


# Confirms you want to reset DB
def confirm():
    user_input = input(
        "Would you like to:\n"
        "1: Clear and repopulate the LionAuction database from scratch using dataset - ** Clears all existing data **\n"
        "2: Add missing data from datasets - ** Will not clear existing data **\n"
        "Type 1 or 2 select you option, any other input will exit\n")

    # Clear and repopulate
    if user_input == "1":
        user_input = input(
            "Are you sure you would like to clear the LionAuction database and repopulate from scratch? Type YES to confirm\n")
        if user_input == "YES":
            print("\nDropping Tables...")
            clear_DB()
            print("\nRepopulating tables...")
            populate_DB()
        else:
            print("Action not confirmed, exiting")

    # Add missing data
    elif user_input == "2":
        print("\nChecking for missing data in tables...")
        populate_DB()
    exit()


# Populate tables in database
def populate_DB():
    populate_user_DB()
    populate_address_DB()
    populate_auction_listings_DB()
    populate_bidders_DB()
    populate_bids_DB()
    populate_categories_DB()
    populate_credit_cards_DB()
    populate_helpdesk_DB()
    populate_local_vendors_DB()
    populate_ratings_DB()
    populate_requests_DB()
    populate_sellers_DB()
    populate_transactions_DB()
    populate_zipcode_info_DB()
    print("\nFinished")
    return


# Drop tables from database
def clear_DB():
    connection = sql.connect('database.db')
    connection.execute('DROP TABLE IF EXISTS address;')
    connection.execute('DROP TABLE IF EXISTS auction_listings;')
    connection.execute('DROP TABLE IF EXISTS bidders;')
    connection.execute('DROP TABLE IF EXISTS bids;')
    connection.execute('DROP TABLE IF EXISTS categories;')
    connection.execute('DROP TABLE IF EXISTS credit_cards;')
    connection.execute('DROP TABLE IF EXISTS helpdesk;')
    connection.execute('DROP TABLE IF EXISTS local_vendors;')
    connection.execute('DROP TABLE IF EXISTS ratings;')
    connection.execute('DROP TABLE IF EXISTS requests;')
    connection.execute('DROP TABLE IF EXISTS sellers;')
    connection.execute('DROP TABLE IF EXISTS transactions;')
    connection.execute('DROP TABLE IF EXISTS users;')
    connection.execute('DROP TABLE IF EXISTS zipcode_info;')
    connection.commit()
    print('Tables dropped')
    return


# Populate user database
def populate_user_DB():
    # Create database
    connection = sql.connect('database.db')
    connection.execute('CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY, password TEXT);')
    connection.commit()

    # Get length of csv file
    with open('LionAuctionDataset/Users.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        total_entries = sum(1 for row in data) - 1

    # Populate database
    with open('LionAuctionDataset/Users.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        parsed_entries = 0
        next(data)
        # Add each entry to database
        for line in data:
            user_email, user_password = line[0], line[1]
            # Check if entry is in database
            cursor = connection.execute('SELECT email FROM users WHERE email=?', (user_email,))
            result = cursor.fetchone()
            if not result:
                hashed_password = hash_password(user_password)
                connection.execute('INSERT INTO users (email, password) VALUES (?,?)', (user_email, hashed_password))
                connection.commit()
            parsed_entries += 1
            print('', end='\rUsers table: ' + str(parsed_entries) + '/' + str(total_entries))
    print("")
    return


# Populate address database
def populate_address_DB():
    # Create database
    connection = sql.connect('database.db')
    connection.execute(
        'CREATE TABLE IF NOT EXISTS address(address_ID TEXT PRIMARY KEY, zipcode INTEGER, street_num INTEGER, street_name TEXT'
        ', FOREIGN KEY (address_ID) REFERENCES bidders(home_address_id) '
        ', FOREIGN KEY (address_ID) REFERENCES local_vendors(Business_Address_ID));')
    connection.commit()

    # Get length of csv file
    with open('LionAuctionDataset/Address.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        total_entries = sum(1 for row in data) - 1

    # Populate database
    with open('LionAuctionDataset/Address.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        parsed_entries = 0
        next(data)
        # Add each entry to database
        for line in data:
            address_ID, zipcode, street_num, street_name = line[0], line[1], line[2], line[3]
            # Check if entry is in database
            cursor = connection.execute('SELECT address_ID FROM address WHERE address_ID=?', (address_ID,))
            result = cursor.fetchone()
            if not result:
                connection.execute(
                    'INSERT INTO address (address_ID, zipcode, street_num, street_name) VALUES (?,?,?,?)',
                    (address_ID, zipcode, street_num, street_name))
                connection.commit()
            parsed_entries += 1
            print('', end='\rAddress table: ' + str(parsed_entries) + '/' + str(total_entries))
    print("")
    return


# Populate auction_listings database
def populate_auction_listings_DB():
    # Create database
    connection = sql.connect('database.db')
    connection.execute('CREATE TABLE IF NOT EXISTS auction_listings('
                       'Seller_Email TEXT, Listing_ID INTEGER, Category TEXT, Auction_Title TEXT, Product_Name TEXT, '
                       'Product_Description TEXT, Quantity INTEGER, Reserve_Price INTEGER, Max_bids INTEGER, Status INTEGER,'
                       'Remove_Reason TEXT,'
                       'PRIMARY KEY (Seller_Email, Listing_ID),'
                       'FOREIGN KEY (Seller_Email) REFERENCES sellers(email));')
    connection.commit()

    # Get length of csv file
    with open('LionAuctionDataset/Auction_Listings.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        total_entries = sum(1 for row in data) - 1

    # Populate database
    with open('LionAuctionDataset/Auction_Listings.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        parsed_entries = 0
        next(data)
        # Add each entry to database
        for line in data:
            Seller_Email, Listing_ID, Category, Auction_Title, Product_Name, Product_Description, Quantity, Reserve_Price, Max_bids, Status = \
                line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7][1:], line[8], line[9]
            # Check if entry is in database
            cursor = connection.execute(
                'SELECT Seller_Email, Listing_ID FROM auction_listings WHERE Seller_Email=? AND Listing_ID=?',
                (Seller_Email, Listing_ID,))
            result = cursor.fetchone()
            if not result:
                connection.execute('INSERT INTO auction_listings '
                                   '(Seller_Email, Listing_ID, Category, Auction_Title, Product_Name, Product_Description, Quantity, Reserve_Price, Max_bids, Status, Remove_Reason) '
                                   'VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                                   (Seller_Email, Listing_ID, Category, Auction_Title, Product_Name,
                                    Product_Description,
                                    Quantity, Reserve_Price, Max_bids, Status, ""))
                connection.commit()
            parsed_entries += 1
            print('', end='\rAuction Listings table: ' + str(parsed_entries) + '/' + str(total_entries))
    print("")
    return


# Populate bidders database
def populate_bidders_DB():
    # Create database
    connection = sql.connect('database.db')
    connection.execute(
        'CREATE TABLE IF NOT EXISTS bidders(email TEXT PRIMARY KEY , first_name TEXT, last_name TEXT, gender TEXT, '
        'age INTEGER, home_address_id TEXT, major TEXT, '
        'FOREIGN KEY (email) REFERENCES users(email));')
    connection.commit()

    # Get length of csv file
    with open('LionAuctionDataset/Bidders.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        total_entries = sum(1 for row in data) - 1

    # Populate database
    with open('LionAuctionDataset/Bidders.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        parsed_entries = 0
        next(data)
        # Add each entry to database
        for line in data:
            email, first_name, last_name, gender, age, home_address_id, major = line[0], line[1], line[2], line[3], \
                line[4], line[5], line[6]
            # Check if entry is in database
            cursor = connection.execute('SELECT email FROM bidders WHERE email=?', (email,))
            result = cursor.fetchone()
            if not result:
                connection.execute(
                    'INSERT INTO bidders (email, first_name, last_name, gender, age, home_address_id, major) VALUES (?,?,?,?,?,?,?)',
                    (email, first_name, last_name, gender, age, home_address_id, major))
                connection.commit()
            parsed_entries += 1
            print('', end='\rBidders table: ' + str(parsed_entries) + '/' + str(total_entries))
    print("")
    return


# Populate bids database
def populate_bids_DB():
    # Create database
    connection = sql.connect('database.db')
    connection.execute(
        'CREATE TABLE IF NOT EXISTS bids(Bid_ID INTEGER PRIMARY KEY, Seller_Email TEXT, Listing_ID INTEGER, Bidder_email TEXT, Bid_price INTEGER,'
        'FOREIGN KEY (Seller_Email) REFERENCES sellers(email),'
        'FOREIGN KEY (Bidder_email) REFERENCES bidders(email),'
        'FOREIGN KEY (Listing_ID) REFERENCES auction_listings(Listing_ID));')
    connection.commit()

    # Get length of csv file
    with open('LionAuctionDataset/Bids.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        total_entries = sum(1 for row in data) - 1

    # Populate database
    with open('LionAuctionDataset/Bids.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        parsed_entries = 0
        next(data)
        # Add each entry to database
        for line in data:
            Bid_ID, Seller_Email, Listing_ID, Bidder_email, Bid_price = line[0], line[1], line[2], line[3], line[4]
            # Check if entry is in database
            cursor = connection.execute('SELECT Bid_ID FROM bids WHERE Bid_ID=?', (Bid_ID,))
            result = cursor.fetchone()
            if not result:
                connection.execute(
                    'INSERT INTO bids (Bid_ID, Seller_Email, Listing_ID, Bidder_email, Bid_price) VALUES (?,?,?,?,?)',
                    (Bid_ID, Seller_Email, Listing_ID, Bidder_email, Bid_price))
                connection.commit()
            parsed_entries += 1
            print('', end='\rBids table: ' + str(parsed_entries) + '/' + str(total_entries))
    print("")
    return


# Populate categories database
def populate_categories_DB():
    # Create database
    connection = sql.connect('database.db')
    connection.execute('CREATE TABLE IF NOT EXISTS categories(parent_category TEXT, category_name TEXT PRIMARY KEY);')
    connection.commit()

    # Get length of csv file
    with open('LionAuctionDataset/Categories.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        total_entries = sum(1 for row in data) - 1

    # Populate database
    with open('LionAuctionDataset/Categories.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        parsed_entries = 0
        next(data)
        # Add each entry to database
        for line in data:
            parent_category, category_name = line[0], line[1]
            # Check if entry is in database
            cursor = connection.execute('SELECT category_name FROM categories WHERE category_name=?', (category_name,))
            result = cursor.fetchone()
            if not result:
                connection.execute('INSERT INTO categories (parent_category, category_name) VALUES (?,?)',
                                   (parent_category, category_name))
                connection.commit()
            parsed_entries += 1
            print('', end='\rCategories table: ' + str(parsed_entries) + '/' + str(total_entries))
    print("")
    return


# Populate credit_cards database
def populate_credit_cards_DB():
    # Create database
    connection = sql.connect('database.db')
    connection.execute(
        'CREATE TABLE IF NOT EXISTS credit_cards(credit_card_num TEXT PRIMARY KEY, card_type TEXT, expire_month INTEGER, '
        'expire_year INTEGER, security_code INTEGER, Owner_email TEXT, '
        'FOREIGN KEY (Owner_email) REFERENCES users(email));')
    connection.commit()

    # Get length of csv file
    with open('LionAuctionDataset/Credit_Cards.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        total_entries = sum(1 for row in data) - 1

    # Populate database
    with open('LionAuctionDataset/Credit_Cards.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        parsed_entries = 0
        next(data)
        # Add each entry to database
        for line in data:
            credit_card_num, card_type, expire_month, expire_year, security_code, Owner_email = line[0], line[1], line[
                2], line[3], line[4], line[5]
            # Check if entry is in database
            cursor = connection.execute('SELECT credit_card_num FROM credit_cards WHERE credit_card_num=?',
                                        (credit_card_num,))
            result = cursor.fetchone()
            if not result:
                connection.execute(
                    'INSERT INTO credit_cards (credit_card_num, card_type, expire_month, expire_year, security_code, Owner_email) VALUES (?,?,?,?,?,?)',
                    (credit_card_num, card_type, expire_month, expire_year, security_code, Owner_email))
                connection.commit()
            parsed_entries += 1
            print('', end='\rCredit cards table: ' + str(parsed_entries) + '/' + str(total_entries))
    print("")
    return


# Populate helpdesk database
def populate_helpdesk_DB():
    # Create database
    connection = sql.connect('database.db')
    connection.execute('CREATE TABLE IF NOT EXISTS helpdesk(email TEXT PRIMARY KEY, position TEXT);')
    connection.commit()

    # Get length of csv file
    with open('LionAuctionDataset/Helpdesk.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        total_entries = sum(1 for row in data) - 1

    # Populate database
    with open('LionAuctionDataset/Helpdesk.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        parsed_entries = 0
        next(data)
        # Add each entry to database
        for line in data:
            email, position = line[0], line[1]
            # Check if entry is in database
            cursor = connection.execute('SELECT email FROM helpdesk WHERE email=?', (email,))
            result = cursor.fetchone()
            if not result:
                connection.execute('INSERT INTO helpdesk (email, position) VALUES (?,?)', (email, position))
                connection.commit()
            parsed_entries += 1
            print('', end='\rHelpdesk table: ' + str(parsed_entries) + '/' + str(total_entries))
    print("")
    return


# Populate local_vendors database
def populate_local_vendors_DB():
    # Create database
    connection = sql.connect('database.db')
    connection.execute('CREATE TABLE IF NOT EXISTS local_vendors(Email TEXT PRIMARY KEY, Business_Name TEXT, '
                       'Business_Address_ID TEXT, Customer_Service_Phone_Number TEXT,'
                       'FOREIGN KEY (Email) REFERENCES sellers(email));')
    connection.commit()

    # Get length of csv file
    with open('LionAuctionDataset/Local_Vendors.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        total_entries = sum(1 for row in data) - 1

    # Populate database
    with open('LionAuctionDataset/Local_Vendors.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        parsed_entries = 0
        next(data)
        # Add each entry to database
        for line in data:
            Email, Business_Name, Business_Address_ID, Customer_Service_Phone_Number = line[0], line[1], line[2], line[
                3]
            # Check if entry is in database
            cursor = connection.execute('SELECT Email FROM local_vendors WHERE Email=?', (Email,))
            result = cursor.fetchone()
            if not result:
                connection.execute(
                    'INSERT INTO local_vendors (Email, Business_Name, Business_Address_ID, Customer_Service_Phone_Number) VALUES (?,?,?,?)',
                    (Email, Business_Name, Business_Address_ID, Customer_Service_Phone_Number))
                connection.commit()
            parsed_entries += 1
            print('', end='\rLocal vendors table: ' + str(parsed_entries) + '/' + str(total_entries))
    print("")
    return


# Populate ratings database
def populate_ratings_DB():
    # Create database
    connection = sql.connect('database.db')
    connection.execute(
        'CREATE TABLE IF NOT EXISTS ratings(Bidder_Email TEXT, Seller_Email TEXT, Date TEXT, Rating INTEGER, Rating_Desc TEXT,'
        'PRIMARY KEY (Bidder_Email, Seller_Email, Date),'
        'FOREIGN KEY (Bidder_Email) REFERENCES transactions(Buyer_Email),'
        'FOREIGN KEY (Seller_Email) REFERENCES  transactions(Seller_Email));')
    connection.commit()

    # Get length of csv file
    with open('LionAuctionDataset/Ratings.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        total_entries = sum(1 for row in data) - 1

    # Populate database
    with open('LionAuctionDataset/Ratings.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        parsed_entries = 0
        next(data)
        # Add each entry to database
        for line in data:
            Bidder_Email, Seller_Email, Date, Rating, Rating_Desc = line[0], line[1], line[2], line[3], line[4]
            # Check if entry is in database
            cursor = connection.execute(
                'SELECT Bidder_Email, Seller_Email, Date FROM ratings WHERE Bidder_Email=? AND Seller_Email=? AND DATE=?',
                (Bidder_Email, Seller_Email, Date,))
            result = cursor.fetchone()
            if not result:
                connection.execute('INSERT INTO ratings (Bidder_Email, Seller_Email, Date, Rating, Rating_Desc) '
                                   'VALUES (?,?,?,?,?)', (Bidder_Email, Seller_Email, Date, Rating, Rating_Desc))
                connection.commit()
            parsed_entries += 1
            print('', end='\rRatings table: ' + str(parsed_entries) + '/' + str(total_entries))
    print("")
    return


# Populate requests database
def populate_requests_DB():
    # Create database
    connection = sql.connect('database.db')
    connection.execute(
        'CREATE TABLE IF NOT EXISTS requests(request_id INTEGER PRIMARY KEY, sender_email TEXT, helpdesk_staff_email TEXT, '
        'request_type TEXT, request_desc TEXT, request_status INTEGER);')
    connection.commit()

    # Get length of csv file
    with open('LionAuctionDataset/Requests.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        total_entries = sum(1 for row in data) - 1

    # Populate database
    with open('LionAuctionDataset/Requests.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        parsed_entries = 0
        next(data)
        # Add each entry to database
        for line in data:
            request_id, sender_email, helpdesk_staff_email, request_type, request_desc, request_status = line[0], line[
                1], line[2], line[3], line[4], line[5]
            # Check if entry is in database
            cursor = connection.execute('SELECT request_id FROM requests WHERE request_id=?', (request_id,))
            result = cursor.fetchone()
            if not result:
                connection.execute(
                    'INSERT INTO requests (request_id, sender_email, helpdesk_staff_email, request_type, request_desc, request_status) VALUES (?,?,?,?,?,?)',
                    (request_id, sender_email, helpdesk_staff_email, request_type, request_desc, request_status))
                connection.commit()
            parsed_entries += 1
            print('', end='\rRequests table: ' + str(parsed_entries) + '/' + str(total_entries))
    print("")
    return


# Populate sellers database
def populate_sellers_DB():
    # Create database
    connection = sql.connect('database.db')
    connection.execute(
        'CREATE TABLE IF NOT EXISTS sellers(email TEXT PRIMARY KEY, bank_routing_number TEXT, bank_account_number INTEGER, balance INTEGER,'
        'FOREIGN KEY (email) REFERENCES users(email));')
    connection.commit()

    # Get length of csv file
    with open('LionAuctionDataset/Sellers.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        total_entries = sum(1 for row in data) - 1

    # Populate database
    with open('LionAuctionDataset/Sellers.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        parsed_entries = 0
        next(data)
        # Add each entry to database
        for line in data:
            email, bank_routing_number, bank_account_number, balance = line[0], line[1], line[2], line[3]
            # Check if entry is in database
            cursor = connection.execute('SELECT email FROM sellers WHERE email=?', (email,))
            result = cursor.fetchone()
            if not result:
                connection.execute(
                    'INSERT INTO sellers (email, bank_routing_number, bank_account_number, balance) VALUES (?,?,?,?)',
                    (email, bank_routing_number, bank_account_number, balance))
                connection.commit()
            parsed_entries += 1
            print('', end='\rSellers table: ' + str(parsed_entries) + '/' + str(total_entries))
    print("")
    return


# Populate transactions database
def populate_transactions_DB():
    # Create database
    connection = sql.connect('database.db')
    connection.execute(
        'CREATE TABLE IF NOT EXISTS transactions(Transaction_ID INTEGER PRIMARY KEY, Seller_Email TEXT, '
        'Listing_ID INTEGER, Buyer_Email TEXT, Date TEXT, Payment INTEGER,'
        'FOREIGN KEY (Seller_Email) REFERENCES auction_listings(Seller_Email),'
        'FOREIGN KEY (Buyer_Email) REFERENCES bidders(email),'
        'FOREIGN KEY (Listing_ID) REFERENCES auction_listings(Listing_ID));')
    connection.commit()

    # Get length of csv file
    with open('LionAuctionDataset/Transactions.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        total_entries = sum(1 for row in data) - 1

    # Populate database
    with open('LionAuctionDataset/Transactions.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        parsed_entries = 0
        next(data)
        # Add each entry to database
        for line in data:
            Transaction_ID, Seller_Email, Listing_ID, Buyer_Email, Date, Payment = line[0], line[1], line[2], line[3], \
            line[4], line[5]
            # Check if entry is in database
            cursor = connection.execute('SELECT Transaction_ID FROM transactions WHERE Transaction_ID=?',
                                        (Transaction_ID,))
            result = cursor.fetchone()
            if not result:
                connection.execute(
                    'INSERT INTO transactions (Transaction_ID, Seller_Email, Listing_ID, Buyer_Email, Date, Payment) VALUES (?,?,?,?,?,?)',
                    (Transaction_ID, Seller_Email, Listing_ID, Buyer_Email, Date, Payment))
                connection.commit()
            parsed_entries += 1
            print('', end='\rTransactions table: ' + str(parsed_entries) + '/' + str(total_entries))
    print("")
    return


# Populate zipcode_info database
def populate_zipcode_info_DB():
    # Create database
    connection = sql.connect('database.db')
    connection.execute(
        'CREATE TABLE IF NOT EXISTS zipcode_info(zipcode INTEGER PRIMARY KEY, city TEXT, state TEXT,'
        'FOREIGN KEY (zipcode) REFERENCES address(zipcode));')
    connection.commit()

    # Get length of csv file
    with open('LionAuctionDataset/Zipcode_Info.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        total_entries = sum(1 for row in data) - 1

    # Populate database
    with open('LionAuctionDataset/Zipcode_Info.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        parsed_entries = 0
        next(data)
        # Add each entry to database
        for line in data:
            zipcode, city, state = line[0], line[1], line[2]
            # Check if entry is in database
            cursor = connection.execute('SELECT zipcode FROM zipcode_info WHERE zipcode=?', (zipcode,))
            result = cursor.fetchone()
            if not result:
                connection.execute(
                    'INSERT INTO zipcode_info (zipcode, city, state) VALUES (?,?,?)',
                    (zipcode, city, state))
                connection.commit()
            parsed_entries += 1
            print('', end='\rZipcode info table: ' + str(parsed_entries) + '/' + str(total_entries))
    print("")
    return


# Securely Hashes Password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=4))


if __name__ == "__main__":
    confirm()
