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
        username = request.form['username']
        password = request.form['password']

        # TODO: Get password from user database
        user_password = "";

        # Perform authentication check
        if bcrypt.checkpw(password.encode('utf-8'), user_password):
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


# TODO: Populate user database
def create_user_DB():
    return


if __name__ == "__main__":
    create_user_DB()
    app.run()
