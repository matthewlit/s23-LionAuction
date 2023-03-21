from flask import Flask, render_template, request
import sqlite3 as sql

app = Flask(__name__)

host = 'http://127.0.0.1:5000/'

#Login Page
@app.route('/')
def index():
    return render_template('login.html')

if __name__ == "__main__":
    app.run()