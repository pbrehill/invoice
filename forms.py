from flask_wtf import FlaskForm
from invoice import User
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

class RegistrationForm(FlaskForm):
    email = StringField('Email',
                        validators= [DataRequired(), Email()])
    password=PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_field(self, field):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('There is already an account for that email')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators= [DataRequired(), Email()])
    password=PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log In')

