# **Lion Auction Progress Review**

## About Me

Matthew Kelleher - mtk5386@psu.edu

## About The Project

The Phase 2 System Prototype for Lion Auction. Allows a registered user to log in to the LionAuction system. Once logged in, bidders can view and bid on various auctions by browsing auction categories and check on the status of their current bids. Sellers can create new auctions to add to the auction listings and edit their current auctions, as well as complete transactions for sold items.

**Note**: This is not a finished product, but a basic implementation of how the LionAuction website should run.  

## Webpage Features

- **Login Page:** Using the users’ log-in information stored in the user table in the database, the system authenticates a user using their username and password and the selected roll. If successful go to the `Welcome Page` for the selected roll, if failed then a message is displayed.

- **Welcome Page:** Displays a user's relevant information depending on roll. Contains buttons to navigate to other relevant operation for the signed in roll. Sign out button returns user back to `Login Page`

- **Auction Listings Page:** Displays all active auction listings for bidders to browse. Bidders can browse by categories or search to find more specific auctions. Each auction has an option to go to the `Bid Page` for more information on the auction and place a bid.

- **Bid Status Page:** Displays all auction listings the bidder has a bid on and their current status, including if the bidder won the auction. All auctions have an option to go to the `Bid Page` for more information on the auction and place a bid if it is active.

- **Bid Page:** Displays all relevant information for the current auction the bidder is viewing. If the auction is active the bidder has the option to place a bid on the item that is $1 higher than the highest bid. If there is no bids then the bid must be at least the auctions reserve price. If the bidder places the highest bid when max bids is reached they win the auction.

- **Auction Status Page:** Displays all auctions a seller has created. Gives the seller the option to edit, activate, deactivate, and complete transactions on auctions depending on their status. Once a transaction is complete a seller can see the winners contact and shipping information. Also includes a section for a seller to create a new auction listing to put up for bidding.

- **Database:** Contains tables outlined in `RelationalSchema.pdf` populated with the data from `LionAuctionDataset`. Tables are stored in `database.db`.

## File Organization

- **templates:** Folder containing HTML templates for the webpages.

- **app.py:** Python script to control the webpages.

- **resetDB.py:** Python script to populate the LionAuction database from dataset.

- **database.db:** Database for the webpage containing LionAuction data.

- **css:** Folder containing .css files for the webpages.

- **LionAuctionDataset:** Folder containing .csv files of the LionAuction dataset.

- **RelationalSchema.pdf:** document containing the rational schema.

- **Phase1_Report.pdf:** Phase 1 report.

## Libraries

- Python3: <https://www.python.org/>
- Flask: <https://flask.palletsprojects.com/>
- SQLite3: <https://sqlite.org/>
- Bcrypt: <https://github.com/pyca/bcrypt/>

## How To Run

1. Open Pycharm Professional

2. In the top toolbar click `File` then `Open` and select the `s23-LionAuction` file from where you saved it

3. Click on `app.py`

4. In the top toolbar click `Run` and then `Run 'app.py'`

5. The bottom terminal should open and read `Running on http://127.0.0.1:5000`, click on the link to open the webpage
