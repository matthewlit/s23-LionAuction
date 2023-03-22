# **Lion Auction Progress Review**

## About Me

>Matthew Kelleher - mtk5386@psu.edu

## About The Project

>The Phase 2 Progress Review for Lion Auction. Allows a registered user to log in to the LionAuction system. The system authenticates the user by their email and password.

## Webpage Features

>- **Login Page:** Using the users’ log-in information stored in the user table in the database, the system authenticates a user using their username and password. If successful go to the `Main Page`, if fails then a message is displayed.
>
>- **Main Page:** Displays a welcome message and user's username. Sign out button returns user back to `Login Page`
>
>- **Database:** Contains `users` table that contains `email` and a securely hashed `password` for each user in the database. Stored in `database.db`.

## File Organization

>- **templates:** Folder containing HTML templates for the webpages.
>
>- **app.py:** Python file to control the webpages and the database.
>
>- **database.db:** Database for the webpage containing user data.
>
>- **css:** Folder containing css files for the webpages.

## How To Run

>1. Open Pycharm Professional
>
>2. In the top toolbar click `File` then `Open` and select the `s23-LionAuction` file from where you saved it
>
>3. Click on `app.py`
>
>4. In the top toolbar click `Run` and then `Run 'app.py'`
>
>5. The bottom terminal should open and read `Running on http://127.0.0.1:5000`, click on the link to open the webpage
