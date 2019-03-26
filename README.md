# droid-catalog
#
# UDACITY Project - Item Catalog Application README

# Program Overview

The following files generate an application to view, create, edit, delete, and
add droids and their accessories from a database.

Included Files

There are three main python files and supporting html files.
> 1.	catalog.py: This python file contains all of the code to view, create,
edit, delete, and add droids and their accessories from a database. It also
validates user information so that registered users have the ability to post,
edit and delete their own droids and the droid's accessories.

> 2.  droid_database_setup.py: This file creates the database schema for the
application.

> 3.	lotsofdroids.py: This file contains the python code to create starter
users, droids, and accessories for the droids for the droid catalog application.

> 4.  html files: Location: /templates: These files are the html file that
render the application.

> 5.  styles.css: Location: /static: Contains the CSS to style the html files.

# Accessing/Opening the application
The python code is to be run from a vagrant or similar command line application.
Place the catalog.py file in the folder (preferably "catalog"), and place the
/static and /templates directories and their contents in the same directory.

Now from the command line type, **python droid_database_setup.py** to initialize the
database.

Type **python lotsofdroids.py** if you would like to pre-populate the database
with dummy user info and their droids/accessories.

From the vagrant (or similar) command line type, **python catalog.py** to start
the application/webserver.

From your favorite browser open the following url: **http://localhost:8000/**

The application will open and you will have the option to login or browse the
existing droids (from the dummy user data if you installed it).

Use the login link in the top right corner of the application to login via
your Google login.  Once logged in you may create, edit, delete, or modify
droids and their accessories that you create.

Note: You are not allowed to modify other user's droids and their associated
accessories.

# Modifications

Feel free to modify this code and styles. Shoot me a note so I can see your new
creation!

# Credits

Bootstrap was used to help with the css portion of this application. Try it
it is a great resouce **https://getbootstrap.com/**
