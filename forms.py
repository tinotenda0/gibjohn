from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(min=6, max=255)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=128)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')

class LoginForm(FlaskForm):
    email =EmailField('Email', validators=[DataRequired(), Email(), Length(min=6, max=255)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=128)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')