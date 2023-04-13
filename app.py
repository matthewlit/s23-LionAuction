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
    cursor = connection.execute('SELECT first_name,last_name,email,age,gender,major,street_num,street_name,city,state,address.zipcode,credit_card_num '
                                'FROM bidders,address,zipcode_info,credit_cards '
                                'WHERE email=? '
                                'AND bidders.home_address_id=address.address_ID '
                                'AND address.zipcode=zipcode_info.zipcode '
                                'AND bidders.email=credit_cards.Owner_email',
                                (username,))
    result = cursor.fetchone()
    data = {"name": result[0] + " " + result[1],
            "email": result[2],
            "roll": "Bidder",
            "age": result[3],
            "gender": result[4],
            "major": result[5].title(),
            "address": str(result[6]) + " " + result[7] + ", " + result[8] + ", " + result[9] + " " + str(result[10]),
            "card": "**** **** **** " + result[11][-4:]}

    return render_template('bidderMain.html', data=data)


# Seller Main Page
@app.route('/sellerMain', methods=['GET', 'POST'])
def sellerMain():
    return render_template('sellerMain.html')


# Help Desk Main Page
@app.route('/helpdeskMain', methods=['GET', 'POST'])
def helpdeskMain():
    return render_template('helpdeskMain.html')


if __name__ == "__main__":
    app.run(debug=True)
