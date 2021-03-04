import os

from flask import Flask, flash, session, redirect, g, render_template, request, jsonify
from secrets import APP_SECRET_KEY, YELP_API_KEY, DOCUMENU_API_KEY
import requests
import math
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import connect_db, db, User, Favorite, Like, Comment, Cart, Cart_Items, Search_History
from forms import LogInForm, SignUpForm

app = Flask(__name__)

CURR_USER_KEY = 'curr_user'
YELP_URL = 'https://api.yelp.com/v3'
DOCUMENU_URL = 'https://api.documenu.com/v2'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgres:///restaurants')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
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
    if g.user:
        flash('Already logged in!','info')
        return redirect(f'/users/{g.user.id}')
    else:
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

# user endpoints
@app.route('/users/<int:user_id>')
def profile(user_id):
    if g.user:
        user = User.query.get_or_404(user_id)
        return render_template('/user/profile.html', user=user)
    flash('Unauthorized Access!, Please Sign In First!','danger')
    return redirect('/login')

@app.route('/users/<int:user_id>/favorites')
def favorites(user_id):
    if not g.user:
        flash('Unauthorized Access! Please Sign In First!','danger')
        return redirect('/login')
    restaurant_ids = [(favorite.business_id) for favorite in g.user.favorites]
    print(g.user.favorites)
    return render_template('/user/favorites.html', user=g.user)


# restaurants endpoints
@app.route('/restaurants')
def search_restaurants():
    """Get Request to Yelp API and return json results"""
    term = request.args.get('term')
    location = request.args.get('location')
    
    res = requests.get(f'{YELP_URL}/businesses/search', params={'term':term, 'location':location, 'limit':5}, headers={'Authorization': f'Bearer {YELP_API_KEY}'})

    return res.json()

@app.route('/restaurants/<business_id>')
def restaurant_details(business_id):
    res = requests.get(f'{YELP_URL}/businesses/{business_id}', headers={'Authorization': f'Bearer {YELP_API_KEY}'})
    business = res.json()
    if (res.json().get('error', None)):
        flash(f'{res.json()["error"]["description"]}', 'danger')
        return redirect('/')
    else:
        
        menu_res = requests.get(f'{DOCUMENU_URL}/restaurants/search/fields', params={'restaurant_phone':business['phone'][2:], 'exact':'true', 'key':f'{DOCUMENU_API_KEY}'})
        if (menu_res.status_code == 404 or menu_res.json().get('totalResults', 0)<1):
            menu = None
        else:
            print(menu_res.json()['data'][0])
            menu = menu_res.json()['data'][0]['menus']
        return render_template('/business/detail.html', business=business, menu=menu, math=math)

# homepage endpoints
@app.route('/')
def home_page():
    if g.user:
        location = g.user.zip_code
    else:
        location = request.args.get('zip_code', None)
    if location:
        res = requests.get(f'{YELP_URL}/businesses/search', params={'term':'restaurants', 'location':location, 'limit':12}, headers={'Authorization': f'Bearer {YELP_API_KEY}'})
        businesses = res.json()['businesses']
        return render_template('home.html', businesses=businesses, zip_code=location, math=math)
    else:
        return render_template('home.html')

@app.route('/search')
def search_results():
    term = request.args.get('term')
    location = request.args.get('location')

    res = requests.get(f'{YELP_URL}/businesses/search', params={'term':term, 'location':location, 'limit':12}, headers={'Authorization': f'Bearer {YELP_API_KEY}'})
    if (res.json().get('error', None)):
        flash(f'{res.json()["error"]["description"]}', 'danger')
        return redirect('/')
    else:
        businesses = res.json()['businesses']
        return render_template('search.html', location=location, term=term, businesses=businesses, math=math)






