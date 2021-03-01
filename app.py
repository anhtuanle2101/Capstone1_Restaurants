import os

from flask import Flask, flash, session, redirect, g, render_template, request, jsonify
from secrets import APP_SECRET_KEY, YELP_API_KEY
import requests
import math
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import connect_db, db
from forms import LogInForm, SignUpForm

app = Flask(__name__)

CURR_USER_KEY = 'curr_user'
YELP_URL = 'https://api.yelp.com/v3'
DOCUMENU = 'https://api.documenu.com/v2'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgres:///restaurants')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', APP_SECRET_KEY)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)

#User login/logout
@app.before_request
def add_user_to_g():
    """Check if the user is logged in, then set the g.user in global `g`."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user_id):
    """Save logged in user to session"""
    session[CURR_USER_KEY] = user_id

def do_logout():
    """Del logged out user out of session"""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

# User routes log-in, sign-up, log-out
@app.route('/login')
def login():
    form = LogInForm()

    return render_template('/user/login.html')

@app.route('/')
def home_page():
    term = 'crawfish'
    location = '30044'
    
    res = requests.get(f'{YELP_URL}/businesses/search', params={'term':term, 'location':location, 'limit':12}, headers={'Authorization': f'Bearer {YELP_API_KEY}'})
    businesses = res.json()['businesses']
    return render_template('home.html', zip_code='30044', businesses=businesses, math=math)

# API requests
@app.route('/restaurants')
def search_restaurants():
    """Get Request to Yelp API and return json results"""
    term = request.args.get('term')
    location = request.args.get('location')
    
    res = requests.get(f'{YELP_URL}/businesses/search', params={'term':term, 'location':location, 'limit':5}, headers={'Authorization': f'Bearer {YELP_API_KEY}'})

    return res.json()








