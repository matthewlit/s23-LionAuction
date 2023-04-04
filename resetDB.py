import sqlite3 as sql
import bcrypt
import csv


# Confirms you want to reset DB
def confirm():
    user_input = input(
        "Are you sure you would like to clear the LionAuction database and repopulate? Type YES to confirm\n")
    if user_input == "YES":
        print("Dropping Tables...")
        clear_user_DB()
        print("Repopulating tables...")
        populate_user_DB()
        print("Finished")
    else:
        print("Action not confirmed, exiting")
        exit()


# Clear user database
def clear_user_DB():
    connection = sql.connect('database.db')
    connection.execute('DROP TABLE IF EXISTS users;')
    connection.commit()
    print('User table dropped')


# Populate user database
def populate_user_DB():
    # Create user database
    connection = sql.connect('database.db')
    connection.execute('CREATE TABLE IF NOT EXISTS users(email TEXT UNIQUE, password TEXT);')
    connection.commit()

    #Get length of csv file
    with open('Users.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        user_total = sum(1 for row in data)-1

    # Populate user database
    with open('Users.csv', 'r') as csv_file:
        data = csv.reader(csv_file)
        num_users = 0
        next(data)
        # Add each user to database
        for line in data:
            user_email, user_password = line[0], line[1]
            # Check if user is in database
            cursor = connection.execute('SELECT email FROM users WHERE email=?', (user_email,))
            result = cursor.fetchone()
            if not result:
                print('', end='\rUsers added: ' + str(num_users) + '/' + str(user_total))
                hashed_password = hash_password(user_password)
                connection.execute('INSERT INTO users (email, password) VALUES (?,?)', (user_email, hashed_password))
                connection.commit()
                num_users += 1
    return


# Securely Hashes Password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


if __name__ == "__main__":
    confirm()
