# Watch List

A project for personal use. 
Uses MySQL database to hold information about movies and series such as title, duration and status (Watched or Not Watched).
If you wish to use the app, download the files, set up your local MySQL database with a username and a password and use them
on the corresponding fields of the python script like so:

    # ---------- CONFIGURE THESE ----------
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'your_username', 
        'password': 'your_password', 
        'database': 'your_schema' 
    }

After setting the database, run the SQL scripts which create the tables required as well as populate the genres table
with the predetermined movie/series genres.

Now, you can run the python script from an IDE or from the command line and use the GUI to:

1) add movies/series to the database
2) update the status of a movie/series by providing its name
3) filter and view the contents of the database

Nothing much really, don't get your hopes up. Enjoy!
