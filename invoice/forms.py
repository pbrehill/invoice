from flask_login import current_user
from flask_wtf import FlaskForm
from invoice.models import User
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange

class RegistrationForm(FlaskForm):
    email = StringField('Email',
                        validators= [DataRequired(), Email()])
    password=PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First name')
    last_name = StringField('Last name')
    abn = StringField('ABN')
    bank_name = StringField('Account name')
    bank_account_num = StringField('Account number')
    bank_bsb = StringField('BSB')

    submit = SubmitField('Submit')


# Not sure how this works with one parametre

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('There is already an account for that email')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators= [DataRequired(), Email()])
    password=PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email',
                        validators= [DataRequired(), Email()])
    password=PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First name')
    last_name = StringField('Last name')
    abn = StringField('ABN')
    bank_name = StringField('Account name')
    bank_num = StringField('Account number')
    bank_bsb = StringField('BSB')
    submit = SubmitField('Submit')


class UpdateForm(FlaskForm):
    email = StringField('Email',
                        validators= [DataRequired(), Email()])
    first_name = StringField('First name')
    last_name = StringField('Last name')
    abn = StringField('ABN')
    bank_name = StringField('Account name')
    bank_num = StringField('Account number')
    bank_bsb = StringField('BSB')

    submit = SubmitField('Submit')


# Not sure how this works with one parametre

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class InvoiceForm(FlaskForm):
    title = StringField('Invoice name', validators=[DataRequired()])
    recipient = StringField('Payer', validators=[DataRequired()])
    amount = IntegerField('Amount', validators=[NumberRange(min=0)])
    submit = SubmitField('Generate invoice')


class UpdateInvoiceForm(FlaskForm):
    title = StringField('Invoice name', validators=[DataRequired()])
    paid = BooleanField('Paid', default=False)
    items = TextAreaField('Items (one item per line)')
    quantities = TextAreaField('Quantities (one quantity per line)')
    prices = TextAreaField('Prices per unit (one price per line)')
    subtotal = StringField('Subtotal')
    gst = StringField('GST if applicable', default='0')
    amount = StringField('Total')
    submit = SubmitField('Update')
    generate_invoice = SubmitField('Generate invoice')

    def validate_row_num(self, quantities, prices, items):
        if len(quantities.data.split("\n")) == len(prices.data.split("\n")) or \
                len(quantities.data.split("\n")) == len(items.data.split("\n")):
            raise ValidationError('Please ensure there is the same number of items, quantities and prices')


class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Submit')