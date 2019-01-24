from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '3732ef508616f5b7631efed5d81922b3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable = False)
    invoices=db.relationship('Invoice', backref='sender', lazy=True)

    def __repr__(self):
        return f"User('{self.email}')"

class Invoice(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable = False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    recipient = db.Column(db.Text)
    amount = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"User('{self.title}', '{self.date_posted}', '{self.recipient}', '{self.amount}')"


invoices_outstanding = [

    {
        'recipient': 'Soothplayers',
        'title': 'MICF20',
        'date': '25/08/20',
        'amount': 200
    },
    {
        'recipient': 'Coaching',
        'title': 'big coach',
        'date': '26/08/21',
        'amount': 50
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts = invoices_outstanding, title = 'Welcome!')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(message='Account created for {0}, please log in'.format(form.email.data), category='success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', title='Log In', form=form)
