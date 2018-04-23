# coding=utf-8

import random, string, httplib2, json, requests

from flask import Flask, render_template, request, redirect, jsonify
from flask import url_for, flash, make_response
from flask import session as login_session

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

from droid_database_setup import Base, Droid, DroidAccessories, User
from flask_httpauth import HTTPBasicAuth

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

""" This file contains all of the python code to run the droid catalog
    application.
"""
auth = HTTPBasicAuth()

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Droid Accessory Application"


""" Connect to Database and create database session """
engine = create_engine('sqlite:///droidaccessorieswithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


""" Create anti-forgery state token """
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


""" Used to connect via Google. """
@app.route('/gconnect', methods=['POST'])
def gconnect():
    """ Validate state token """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    """ Obtain authorization code """
    code = request.data

    try:
        """ Upgrade the authorization code into a credentials object """
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    """ Check that the access token is valid. """
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    """ If there was an error in the access token info, abort. """
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    """ Verify that the access token is used for the intended user. """
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    """ Verify that the access token is valid for this app. """
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    """ Store the access token in the session for later use. """
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    """ Get user info """
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    """ Determine if user exists, if it doesn't make a new one """
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px; " '
    output += ' "-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


""" User Helper Functions """
def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


""" DISCONNECT - Revoke a current user's token and reset their login_session """
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


""" JSON API to show all droids """
@app.route('/droid/JSON')
def droidsJSON():
    droids = session.query(Droid).all()
    return jsonify(droids=[d.serialize for d in droids])


""" JSON API to view all Droid info """
@app.route('/droid/<int:droid_id>/item/JSON')
def droidItemsJSON(droid_id):
    droid = session.query(Droid).filter_by(id=droid_id).one()
    items = session.query(DroidAccessories).filter_by(
        droid_id=droid_id).all()
    return jsonify(DroidAccessories=[i.serialize for i in items])


""" JSON API to view one specific Droid's accessories """
@app.route('/droid/<int:droid_id>/item/<int:item_id>/JSON')
def accessoryJSON(droid_id, item_id):
    Droid_Accessory = session.query(
        DroidAccessories).filter_by(id=item_id).one()
    return jsonify(Droid_Accessory=Droid_Accessory.serialize)


""" Show all droids """
@app.route('/')
@app.route('/droid')
def showDroids():
    droids = session.query(Droid).order_by(asc(Droid.name))
    items = session.query(DroidAccessories).all()
    if 'username' not in login_session:
        return render_template(
            'publicdroids.html',
            droids = droids,
            items = items)
    else:
        return render_template('droids.html', droids = droids, items = items)


""" Show all droids, and the selected droid with it's accessories. """
@app.route('/droid/<int:droid_id>/selectdroid')
def showSelectedDroid(droid_id):
  allDroids = session.query(Droid).order_by(asc(Droid.name))
  selectedDroid = session.query(Droid).filter_by(id=droid_id).one()
  creator = getUserInfo(selectedDroid.user_id)
  items = session.query(DroidAccessories).filter_by(droid_id=droid_id).all()
  if 'username' not in login_session or creator.id != login_session['user_id']:
    return render_template('publicdroidselected.html',
      items=items,
      allDroids = allDroids,
      selectedDroid = selectedDroid,
      creator = creator)
  else:
    return render_template('droidselected.html',
      items=items,
      allDroids = allDroids,
      selectedDroid = selectedDroid,
      creator = creator)


""" Show a droid with it's accessories (if they have them) """
@app.route('/droid/<int:droid_id>/')
@app.route('/droid/<int:droid_id>/accessories/')
def showItem(droid_id):
  droid = session.query(Droid).filter_by(id=droid_id).one()
  creator = getUserInfo(droid.user_id)
  items = session.query(DroidAccessories).filter_by(
    droid_id=droid_id).all()
  if 'username' not in login_session or creator.id != login_session['user_id']:
    return render_template(
      'publicaccessorylist.html',
      items=items,
      droid=droid,
      creator=creator)
  else:
    return render_template(
      'accessorylist.html',
      items=items,
      droid=droid,
      creator=creator)


""" Create a new droid """
@app.route('/droid/new/', methods=['GET', 'POST'])
def newDroid():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newDroid = Droid(
            name=request.form['name'],
            droid_type=request.form['droid_type'],
            user_id=login_session['user_id'])
        session.add(newDroid)
        flash('New Droid %s Successfully Created' % newDroid.name)
        session.commit()
        return redirect(url_for('showDroids'))
    else:
        return render_template('newdroid.html')


""" Edit a droid """
@app.route('/droid/<int:droid_id>/edit/', methods=['GET', 'POST'])
def editDroid(droid_id):
    editedDroid = session.query(
        Droid).filter_by(id=droid_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedDroid.user_id != login_session['user_id']:
        message = ""
        script += "<script>function myFunction() {alert('You are not "
        script += "authorized to edit this droid. Please create your own droid"
        script += "in order to edit.');}</script><body onload='myFunction()'>"
        return message
    if request.method == 'POST':
        if request.form['name']:
            editedDroid.name = request.form['name']
            flash('Droid Successfully Edited %s' % editedDroid.name)
            return redirect(url_for('showDroids'))
    else:
        return render_template('editdroid.html', droid=editedDroid)


""" Create a new droid accessory """
@app.route('/droid/<int:droid_id>/accessory/new/', methods=['GET', 'POST'])
def newDroidAccessory(droid_id):
    if 'username' not in login_session:
        print "username not in login_session"
        return redirect('/login')
    droid = session.query(Droid).filter_by(id=droid_id).one()
    if login_session['user_id'] != droid.user_id:
        message = ""
        script += "<script>function myFunction() {alert('You are not "
        script += "authorized to add accessories this droid. Please create "
        script += "your own droid in order to add items.');}"
        script += "</script><body onload='myFunction()'>"
        return message
        print "login_session['user_id'] == droid.user_id"
    if request.method == 'POST':
        newAccessory = DroidAccessories(
            name=request.form['name'],
            description=request.form['description'],
            accessory_type=request.form['accessory_type'],
            droid_id=droid_id,
            user_id=droid.user_id)
        session.add(newAccessory)
        session.commit()
        flash('New Menu %s Item Successfully Created' % (newAccessory.name))
        return redirect(url_for('showItem', droid_id=droid_id))
    else:
        return render_template('newdroidaccessory.html', droid_id=droid_id)

""" Edit droid accessory """
@app.route('/droid/<int:droid_id>/accessory/<int:item_id>/edit',
    methods=['GET', 'POST'])
def editDroidAccessory(droid_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(DroidAccessories).filter_by(id=item_id).one()
    droid = session.query(Droid).filter_by(id=droid_id).one()
    if login_session['user_id'] != droid.user_id:
        return redirect(url_for('showItem', droid_id=droid_id))
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
            print editedItem.name
        if request.form['description']:
            editedItem.description = request.form['description']
            print editedItem.description
        if request.form['accessory_type']:
            editedItem.accessory_type = request.form['accessory_type']
            print editedItem.accessory_type
        session.add(editedItem)
        session.commit()
        flash('Droid Accessory Successfully Edited')
        return redirect(url_for('showItem', droid_id=droid_id))
    else:
        print editedItem.accessory_type
        return render_template(
            'editdroiditem.html',
            droid_id=droid_id,
            item_id=item_id,
            item=editedItem)


""" Delete a droid accessory """
@app.route('/droid/<int:droid_id>/accessory/<int:item_id>/delete',
    methods=['GET', 'POST'])
def deleteDroidAccessory(droid_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    droid = session.query(Droid).filter_by(id=droid_id).one()
    itemToDelete = session.query(DroidAccessories).filter_by(id=item_id).one()
    if login_session['user_id'] != droid.user_id:
        message = ""
        script += "<script>function myFunction() {alert('You are not "
        script += "authorized to delete these accessories. Please create "
        script += "your own droid in order to add and delete items.');}"
        script += "</script><body onload='myFunction()'>"
        return message
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Accessory Successfully Deleted')
        return redirect(url_for('showItem', droid_id=droid_id))
    else:
        return render_template(
            'deletedroidaccessory.html', droid_id=droid_id, item=itemToDelete)


""" Disconnect (based on provider, but none yet except Google) """
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showDroids'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showDroids'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
