from flask import Flask, render_template, request
import sqlite3 as sql
import bcrypt
import csv

app = Flask(__name__)

host = 'http://127.0.0.1:5000/'


# Login Page
@app.route('/', methods=['GET', 'POST'])
def login():
    # On login button press
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Gets hashed password from user database
        connection = sql.connect('database.db')
        cursor = connection.execute('SELECT password FROM users WHERE email=?', (username,))
        result = cursor.fetchone()

        # Perform authentication check
        if result != None and bcrypt.checkpw(password.encode('utf-8'), result[0]):
            return render_template('main.html', error=None, result=username)
        else:
            return render_template('login.html', error='Invalid Login: Try Again')

    return render_template('login.html')


# Main Page
@app.route('/main', methods=['GET', 'POST'])
def main():
    return render_template('main.html')


# Securely Hashes Password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


# Populate user database
def populate_user_DB():
    # Create user database
    connection = sql.connect('database.db')
    connection.execute('CREATE TABLE IF NOT EXISTS users(email TEXT UNIQUE, password TEXT);')
    connection.commit()

    # Populate user database
    with open('Users.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        next(data)
        # Add each user to database
        for line in data:
            user_email, user_password = line[0], line[1]
            # Check if user is in database
            cursor = connection.execute('SELECT email FROM users WHERE email=?', (user_email,))
            result = cursor.fetchone()
            if not result:
                print("New user added " + user_email)
                hashed_password = hash_password(user_password)
                connection.execute('INSERT INTO users (email, password) VALUES (?,?)', (user_email, hashed_password))
                connection.commit()
    return


if __name__ == "__main__":
    populate_user_DB()
    app.run()
