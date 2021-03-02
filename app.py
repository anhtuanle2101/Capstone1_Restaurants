import os

from flask import Flask, flash, session, redirect, g, render_template, request, jsonify
from secrets import APP_SECRET_KEY, YELP_API_KEY
import requests
import math
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import connect_db, db, User, Favorite, Like, Comment, Cart, Cart_Items, Search_History
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

#toolbar = DebugToolbarExtension(app)

connect_db(app)

#User login/logout
@app.before_request
def add_user_to_g():
    """Check if the user is logged in, then set the g.user in global `g`."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):
    """Save logged in user to session"""
    session[CURR_USER_KEY] = user.id

def do_logout():
    """Del logged out user out of session"""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

# User routes log-in, sign-up, log-out
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LogInForm()

    if form.validate_on_submit():
        user = User.authenticate(
            email=form.email.data,
            password=form.password.data
        )
        if user:
            do_login(user)
            flash(f'Welcome {user.first_name} {user.last_name}!','success')
            return redirect('/')
        
        flash('Invalid Credentials', 'danger')
    
    return render_template('/user/login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = SignUpForm()

    if form.validate_on_submit():
        try:
            newUser = User.signup(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                password=form.password.data,
                email=form.email.data,
                birth_date=form.birth_date.data or None,
                zip_code=form.zip_code.data,
                image_url=form.image_url.data or User.image_url.default.arg
            )
            db.session.commit()
        except IntegrityError:
            flash('Your Email Is Already Used to Signed Up','danger')
            return render_template('/user/register.html', form=form)
        
        do_login(newUser)
        return redirect('/')
    else:
        return render_template('/user/register.html', form=form)

@app.route('/logout', methods=['POST'])
def logout():
    do_logout()
    
    flash('Log out Successfully', 'success')
    return redirect('/')

@app.route('/')
def home_page():
    if g.user:
        location = g.user.zip_code
        res = requests.get(f'{YELP_URL}/businesses/search', params={'term':'restaurants', 'location':location, 'limit':12}, headers={'Authorization': f'Bearer {YELP_API_KEY}'})
        businesses = res.json()['businesses']
        return render_template('home.html', businesses=businesses, zip_code=location, math=math)

@app.route('/search')
def search_results():
    term = request.args.get('term')
    location = request.args.get('location')

    res = requests.get(f'{YELP_URL}/businesses/search', params={'term':term, 'location':location, 'limit':12}, headers={'Authorization': f'Bearer {YELP_API_KEY}'})
    businesses = res.json()['businesses']
    return render_template('search.html', location=location, term=term, businesses=businesses, math=math)

# API requests
@app.route('/restaurants')
def search_restaurants():
    """Get Request to Yelp API and return json results"""
    term = request.args.get('term')
    location = request.args.get('location')
    
    res = requests.get(f'{YELP_URL}/businesses/search', params={'term':term, 'location':location, 'limit':5}, headers={'Authorization': f'Bearer {YELP_API_KEY}'})

    return res.json()








