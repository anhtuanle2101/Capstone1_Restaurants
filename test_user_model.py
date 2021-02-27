import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from models import db, User, Favorite, Comment, Like

# Set database url var in enviroment variables to a database url for testing
# purposes only
os.environ['DATABASE_URL'] = "postgres:///restaurants-test"

from app import app

db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):
    """Testing user model"""

    def setUp(self):
        """Create a user model, test client"""
        db.session.rollback()
        User.query.delete()

        self.client = app.test_client()
        u = User(
            email="test@test.com",
            first_name='ABC',
            last_name='XYZ',
            zip_code='30032',
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
        self.user = u
    
    
    def test_user_model(self):
        """Is the test user model created, and relationship works with other models"""

        self.assertEqual(len(self.user.comments), 0)
        self.assertEqual(len(self.user.likes), 0)
        self.assertEqual(len(self.user.favorites), 0)

    def test_repr(self):
        """Does the repr method work as expected?"""

        self.assertEqual(self.user.__repr__(), f'<User {self.user.id} {self.user.first_name} {self.user.last_name} {self.user.email} {self.user.zip_code} {self.user.birth_date}>')

    
    def test_create(self):
        """Does User.create successfully create a new user given valid credentials?"""
        u2 = User.signup(
            email="test2@test.com",
            first_name='XYZ',
            last_name='ABC',
            password="HASHED_PASSWORD2",
            zip_code='30022'
        )
        db.session.commit()
    
        self.assertIn(u2, User.query.all())
        
    # Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?
    def test_create_fail(self):
        """User.create fails to create a new user if any of the validations?"""
        u2 = User(
            email='test@test.com',
            first_name='XYZ',
            last_name='ABC',
            password='HASHED_PASSWORD2',
            zip_code='30022'
        )
        db.session.add(u2)
        try:
            db.session.commit()
        except IntegrityError as E:
            self.assertRaises(IntegrityError)