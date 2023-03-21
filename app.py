from flask import Flask, render_template, request
import sqlite3 as sql

app = Flask(__name__)

host = 'http://127.0.0.1:5000/'


# Login Page
@app.route('/', methods=['GET', 'POST'])
def login():
    # On login button press
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Perform authentication check
        if username == 'username' and password == 'password':
            return render_template('main.html', error=None, result=username)
        else:
            return render_template('login.html', error='Invalid Login: Try Again')

    return render_template('login.html')


# Main Page
@app.route('/main', methods=['GET', 'POST'])
def main():
    return render_template('main.html')


if __name__ == "__main__":
    app.run()
