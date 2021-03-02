from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    """User collection in the system."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    zip_code = db.Column(db.String(5), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    birth_date = db.Column(db.DateTime)
    image_url = db.Column(db.Text, nullable=False, default='/static/images/default-pic.png')

    favorites = db.relationship('Favorite')
    
    comments = db.relationship('Comment')

    likes = db.relationship('Like')

    searches = db.relationship('Search_History')

    carts = db.relationship('Cart')

    def __repr__(self):
        return f'<User {self.id} {self.first_name} {self.last_name} {self.email} {self.zip_code} {self.birth_date}>'

    @classmethod
    def signup(cls, first_name, last_name, password, email, birth_date, zip_code, image_url):
        u = cls.query.filter(User.email == email).first()
        if u:
            return False
        else:
            hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
            u = cls(
                first_name= first_name,
                last_name= last_name,
                password= hashed_pwd,
                email= email,
                birth_date=birth_date or None,
                zip_code= zip_code,
                image_url= image_url
            )
            db.session.add(u)
            return u
    
    @classmethod
    def authenticate(cls, email, password):
        u = User.query.filter(User.email == email).first()
        if u:
            is_auth = bcrypt.check_password_hash(u.password, password)
            if is_auth:
                return u
        return False
    

class Favorite(db.Model):
    """Favorites collection => users can favorites businesses"""

    __tablename__ = 'favorites'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    business_id = db.Column(db.Text, primary_key=True)

    user = db.relationship('User')

class Comment(db.Model):
    """Comments collection => Users can comment on businesses"""

    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)
    business_id = db.Column(db.Text, nullable=False)

    user = db.relationship('User')

    likes = db.relationship('Like')
    
class Like(db.Model):
    """Likes collection => Users can like comments on businesses"""

    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id', ondelete='cascade'), nullable=False)

    user = db.relationship('User')
    comment = db.relationship('Comment')

class Cart(db.Model):
    """Collection of carts that a user associate with"""
    
    __tablename__ = "carts"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)

    user = db.relationship('User')

class Cart_Items(db.Model):
    """Cart of items Collection which each user have history of carts of items"""

    __tablename__ = 'cart_items'

    item_id = db.Column(db.Integer, db.ForeignKey('carts.id', ondelete='cascade'), primary_key=True)
    cart_id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

class Search_History(db.Model):
    """Search history Collection"""

    __tablename__ = 'searches'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    term = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)

    user = db.relationship('User')