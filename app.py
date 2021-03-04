import os

from flask import Flask, flash, session, redirect, g, render_template, request, jsonify
from secrets import APP_SECRET_KEY, YELP_API_KEY, DOCUMENU_API_KEY
import requests
import math
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import connect_db, db, User, Favorite, Like, Comment, Cart, Cart_Items, Search_History, Business
from forms import LogInForm, SignUpForm, CommentForm, SearchForm

app = Flask(__name__)

CURR_USER_KEY = 'curr_user'
YELP_URL = 'https://api.yelp.com/v3'
DOCUMENU_URL = 'https://api.documenu.com/v2'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgres:///restaurants')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', APP_SECRET_KEY)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

#toolbar = DebugToolbarExtension(app)

connect_db(app)

# Helper methods
def scrape_business(business_id):
    ''' Scrape the business with the business_id from the YELP database into local database for querying '''
    res = requests.get(f'{YELP_URL}/businesses/{business_id}', headers={'Authorization': f'Bearer {YELP_API_KEY}'})
    business_json = res.json()
    if (res.json().get('error', None)):
        flash(f'{res.json()["error"]["description"]}', 'danger')
        return None
    else:
        new_location = f'{business_json["location"]["address1"]}, {business_json["location"]["city"]} {business_json["location"]["state"]} {business_json["location"]["zip_code"]}'
        new_hours = ''
        if business_json['hours']:
            for hour in business_json["hours"][0]["open"]:
                new_hours += f"{hour['day']}{hour['start']}{hour['end']},"
        new_business = Business(
            id=business_json['id'],
            name=business_json['name'],
            image_url=business_json['image_url'],
            url=business_json['url'],
            phone=business_json['phone'][2:],
            rating=business_json['rating'],
            location=new_location,
            price=business_json.get('price', None),
            hours=new_hours
        )
        db.session.add(new_business)
        db.session.commit()
        return new_business

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
    '''Login Page'''
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
    '''Register Page'''
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
        flash('Registered Successfully!', 'success')
        return redirect('/')
    else:
        return render_template('/user/register.html', form=form)

@app.route('/logout', methods=['POST'])
def logout():
    '''Logout'''
    do_logout()

    flash('Log out Successfully', 'success')
    return redirect('/')

# user endpoints
@app.route('/users/<int:user_id>')
def profile(user_id):
    '''User Account Page'''
    if g.user:
        user = User.query.get_or_404(user_id)
        return render_template('/user/profile.html', user=user)
    flash('Unauthorized Access!, Please Sign In First!','danger')
    return redirect('/login')

@app.route('/users/<int:user_id>/favorites')
def favorites(user_id):
    '''User Favorites Page'''
    if not g.user:
        flash('Unauthorized Access! Please Sign In First!','danger')
        return redirect('/login')
    businesses = g.user.favorites
    favorites = [(favorite.id) for favorite in g.user.favorites]
    return render_template('/user/favorites.html', user=g.user, businesses=businesses, favorites=favorites, math=math)

@app.route('/users/add_favorite/<business_id>', methods=['POST'])
def add_favorite(business_id):
    '''Add A Favorite Restaurant'''
    if not g.user:
        flash('Unauthorized Access! Please Sign In First!','danger')
        return redirect('/login')
    business = Business.query.get(business_id)
    if not business:
        new_business = scrape_business(business_id)
        if new_business:
            g.user.favorites.append(new_business)
            db.session.commit()
        return redirect('/')
    else:
        g.user.favorites.append(business)
        return redirect('/')
    
@app.route('/users/remove_favorite/<business_id>', methods=['POST'])
def remove_favorite(business_id):
    '''Remove A Favorited Restaurant'''
    if not g.user:
        flash('Unauthorized Access! Please Sign In First!', 'danger')
        return redirect('/login')
    business = Business.query.get(business_id)
    if business in g.user.favorites:
        g.user.favorites.remove(business)
        db.session.commit()
        return redirect('/')
    else:
        return redirect('/')


# restaurants endpoints
@app.route('/restaurants')
def search_restaurants():
    """Get Request to Yelp API and return json results"""
    term = request.args.get('term')
    location = request.args.get('location')
    
    res = requests.get(f'{YELP_URL}/businesses/search', params={'term':term, 'location':location, 'limit':5}, headers={'Authorization': f'Bearer {YELP_API_KEY}'})

    return res.json()

@app.route('/restaurants/<business_id>', methods=['GET','POST'])
def restaurant_details(business_id):
    '''Restaurant Details'''
    business = Business.query.get(business_id)
    if not business:
        new_business = scrape_business(business_id)
        if new_business:
            business = new_business
        else:
            redirect('/')
    menu_res = requests.get(f'{DOCUMENU_URL}/restaurants/search/fields', params={'restaurant_phone':business.phone[2:], 'exact':'true', 'key':f'{DOCUMENU_API_KEY}'})
    if (menu_res.status_code == 404 or menu_res.json().get('totalResults', 0)<1):
        menu = None
    else:
        menu = menu_res.json()['data'][0]['menus']
    if not g.user:
        return render_template('/business/detail.html', comment_form=None, business=business, menu=menu, math=math)
    else:
        comment_form = CommentForm()
        if comment_form.validate_on_submit():
            new_comment = Comment(
                message=comment_form.message.data,
                user_id=g.user.id,
                business_id=business.id
            )
            db.session.add(new_comment)
            db.session.commit()
            return redirect(f'/restaurants/{business.id}')
        else:
            hours = business.hours.split(',')
            comments = business.comments
            return render_template('/business/detail.html', comment_form=comment_form, business=business, hours=hours, comments=comments, menu=menu, math=math)

# homepage endpoints
@app.route('/')
def home_page():
    if g.user:
        location = g.user.zip_code
    else:
        location = request.args.get('zip_code', None)
    search_form= SearchForm()
    if location:
        res = requests.get(f'{YELP_URL}/businesses/search', params={'term':'restaurants', 'location':location, 'limit':12}, headers={'Authorization': f'Bearer {YELP_API_KEY}'})
        businesses = res.json()['businesses']
        favorites = [(favorite.id) for favorite in g.user.favorites]
        return render_template('home.html', search_form=search_form, businesses=businesses, favorites=favorites, zip_code=location, math=math)
    else:
        return render_template('home.html', search_form=search_form)

@app.route('/search', methods=['GET','POST'])
def search_results():
    search_form= SearchForm()
  
    if search_form.validate_on_submit():
        term = search_form.term.data
        location = search_form.location.data
        res = requests.get(f'{YELP_URL}/businesses/search', params={'term':term, 'location':location, 'limit':12}, headers={'Authorization': f'Bearer {YELP_API_KEY}'})
        if (res.json().get('error', None)):
            flash(f'{res.json()["error"]["description"]}', 'danger')
            return redirect('/')
        else:
            businesses = res.json()['businesses']
            return render_template('search.html', search_form=search_form, location=location, term=term, businesses=businesses, math=math)
    else:
        return render_template('search.html', search_form=search_form)






