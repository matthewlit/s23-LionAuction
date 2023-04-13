from flask import Flask, render_template, request
import sqlite3 as sql
import bcrypt

app = Flask(__name__)

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
            cursor = connection.execute('SELECT password FROM users,bidders WHERE users.email=? AND users.email=bidders.email',
                                        (username,))
        elif roll == 'seller':
            cursor = connection.execute('SELECT password FROM users,sellers WHERE users.email=? AND users.email=sellers.email',
                                        (username,))
        elif roll == 'helpdesk':
            cursor = connection.execute('SELECT password FROM users,helpdesk WHERE users.email=? AND users.email=helpdesk.email',
                                        (username,))
        result = cursor.fetchone()

        # Perform authentication check
        if result is not None and bcrypt.checkpw(password.encode('utf-8'), result[0]):
            if roll == 'bidder':
                return render_template('bidderMain.html', error=None, result=username)
            elif roll == 'seller':
                return render_template('sellerMain.html', error=None, result=username)
            elif roll == 'helpdesk':
                return render_template('helpdeskMain.html', error=None, result=username)
        else:
            return render_template('login.html', error='Invalid Login: Try Again')

    return render_template('login.html')


# Bidder Main Page
@app.route('/bidderMain', methods=['GET', 'POST'])
def bidderMain():
    return render_template('bidderMain.html')


# Seller Main Page
@app.route('/sellerMain', methods=['GET', 'POST'])
def sellerMain():
    return render_template('sellerMain.html')


# Help Desk Main Page
@app.route('/helpdeskMain', methods=['GET', 'POST'])
def helpdeskMain():
    return render_template('helpdeskMain.html')


if __name__ == "__main__":
    app.run()
