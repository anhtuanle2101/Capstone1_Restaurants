from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField
from wtforms.validators import Length, DataRequired, Email, Optional

NAME_VALIDATOR_MSG = 'Length is out of range (50 chars max)'
EMAIL_VALIDATOR_MSG = 'Must be a valid E-mail!'
PASSWORD_VALIDATOR_MSG = 'Length must be in range 6-30'
ZIPCODE_VALIDATOR_MSG = 'Length must be 5'

class SignUpForm(FlaskForm):
    
    first_name = StringField('First Name', validators=[DataRequired(), Length(message=NAME_VALIDATOR_MSG, min=1, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(message=NAME_VALIDATOR_MSG, min=1, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(message=EMAIL_VALIDATOR_MSG)])
    password = PasswordField('Password', validators=[DataRequired(), Length(message=PASSWORD_VALIDATOR_MSG, min=6, max=30)])
    zip_code = StringField('Zip Code', validators=[DataRequired(), Length(min=5, max=5, message=ZIPCODE_VALIDATOR_MSG)])
    birth_date = DateField('Birth Date(Optional)', validators=[Optional()])
    image_url = StringField('Image URL')

class LogInForm(FlaskForm):
    
    email = StringField('Email', validators=[DataRequired(), Email(message=EMAIL_VALIDATOR_MSG)])
    password = PasswordField('Password', validators=[DataRequired(), Length(message=PASSWORD_VALIDATOR_MSG, min=6, max=30)])
