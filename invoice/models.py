from datetime import datetime
from invoice import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable = False)
    invoices = db.relationship('Invoice', backref='sender', lazy=True)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    bank_name = db.Column(db.String)
    bank_num = db.Column(db.String)
    bank_bsb = db.Column(db.String)
    abn = db.Column(db.String)

    def __repr__(self):
        return f"User('{self.email}')"


class Invoice(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable = False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    recipient = db.Column(db.Text)
    amount = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), default=False, nullable=False)
    paid = db.Column(db.Boolean, default=False)
    items = db.Column(db.Text)
    quantities = db.Column(db.Text)
    prices = db.Column(db.Text)
    subtotal = db.Column(db.Text)
    gst = db.Column(db.Text)

    def __repr__(self):
        return f"User('{self.title}', '{self.date_posted}', '{self.recipient}', '{self.amount}')"

# TODO: Build a recipients database
