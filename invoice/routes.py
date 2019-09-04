from datetime import datetime
from flask import render_template, url_for, flash, redirect, request
from invoice import app, bcrypt, login_manager, db
from invoice.forms import RegistrationForm, LoginForm, UpdateForm, InvoiceForm, UpdateInvoiceForm, SearchForm
from invoice.models import User, Invoice
from invoice.searchalg import search_invoices
from flask_login import login_user, current_user, logout_user, login_required
from random import randint
import pandas as pd
import numpy as np



# TODO: Highlight overdue with bootstrap
# TODO: Recipients as relationship
# TODO: Invoice -> html -> PDF
# TODO: Dropdown field for recipient

@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        invoices_outstanding = Invoice.query.filter_by(user_id=current_user.id).order_by(Invoice.date_posted.desc()).all()
    else:
        invoices_outstanding = []
    return render_template('home.html', posts = invoices_outstanding, title = 'Welcome!')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=form.email.data, password=hashed_password, first_name = form.first_name.data, last_name = form.last_name.data,
                    abn=form.abn.data, bank_num=form.bank_num.data, bank_name=form.bank_name.data, bank_bsb=form.bank_bsb.data)
        db.session.add(user)
        db.session.commit()
        flash(message='Account created for {0}'.format(form.email.data), category='success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(url_for(next_page[1:])) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Log In', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateForm()
    if form.validate_on_submit():
        current_user.email=form.email.data
        current_user.first_name=form.first_name.data
        current_user.last_name=form.last_name.data
        current_user.abn=form.abn.data
        current_user.bank_num=form.bank_num.data
        current_user.bank_name=form.bank_name.data
        current_user.bank_bsb=form.bank_bsb.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.abn.data = current_user.abn
        form.bank_num.data = current_user.bank_num
        form.bank_name.data = current_user.bank_name
        form.bank_bsb.data = current_user.bank_bsb

    return render_template('account.html', title='Account', form=form)


@app.route("/invoice/new", methods=['GET', 'POST'])
@login_required
def create_invoice():
    form = InvoiceForm()
    if form.validate_on_submit():
        invoice = Invoice(title=form.title.data, recipient=form.recipient.data, amount=form.amount.data,
                          user_id=current_user.id, id=randint(100000000000,999999999999))
        # TODO: Ensure no chance override of invoice id
        db.session.add(invoice)
        db.session.commit()
        flash('Your invoice has been created', 'success')
        return redirect(url_for('home'))
    return render_template('create_invoice.html', title='New Invoice', form=form)


@app.route("/invoice/<invoice_id>", methods=['GET', 'POST'])
def invoice(invoice_id):
    post = Invoice.query.get_or_404(invoice_id)
    form = UpdateInvoiceForm()
    # TODO: Reconcile this with sums in invoice print
    if current_user.is_authenticated and current_user.id == post.user_id:
        if form.validate_on_submit():
            post.title = form.title.data
            post.items=form.items.data
            items_list = post.items.split("\n")
            post.quantities=form.quantities.data
            quantities_list = post.quantities.split("\n")
            post.prices = form.prices.data
            prices_list = post.prices.split("\n")
            subtotal_price = '0'

            if len(quantities_list) != len(prices_list) or \
                len(quantities_list) != len(items_list):
                flash('Make sure you have the same number of items, prices and quantities', 'danger')
            elif len(quantities_list) + len(prices_list) + len(items_list) != 0:
                try:
                    for i in range(len(prices_list)):
                        subtotal_price = str(int(subtotal_price) + (int(prices_list[i]) * int(quantities_list[i])))
                    post.subtotal = subtotal_price
                    post.gst=form.gst.data
                    post.amount = str(int(post.gst) + int(subtotal_price))
                    post.paid=form.paid.data
                    db.session.commit()
                    flash('Your invoice has been updated', 'success')
                except ValueError:
                    flash('Make sure you entered only numbers into the price and quantity fields (no dollar signs)', 'danger')
        elif request.method == 'GET':
            form.title.data = post.title
            form.items.data = post.items
            form.quantities.data = post.quantities
            form.prices.data = post.prices
            form.subtotal.data = post.subtotal
            form.gst.data = post.gst
            form.amount.data = post.amount
            form.paid.data = post.paid
        return render_template('invoice_page.html', title=post.title, post=post, form=form, invoice_id=invoice_id)
    else:
        flash(f'You do not have permission to view Invoice ID:{invoice_id}', 'danger')
        return redirect(url_for('home'))

@app.route("/invoice/<invoice_id>/print", methods=['GET', 'POST'])
def print_invoice(invoice_id):
    post = Invoice.query.get_or_404(invoice_id)
    user = current_user
    items=post.items.split("\n")
    quantities=post.quantities.split("\n")
    quantities = [int(x) for x in quantities]
    prices = post.prices.split("\n")
    prices = [int(x) for x in prices]
    tuples = zip(items, quantities, prices)



    if current_user.is_authenticated and user.id == post.user_id:
        return render_template('invoice_print.html', title=post.title, post=post, user=user, tuples=tuples,
                               subtotal_price=int(post.subtotal), gst=int(post.gst))
    else:
        flash(f'You do not have permission to view Invoice ID:{invoice_id}', 'danger')
        return redirect(url_for('home'))

@app.route("/search", methods=['GET', 'POST'])
def search():
    searched_invoices = []
    form = SearchForm()
    if form.validate_on_submit():
        searched_invoices = list(search_invoices(form.query.data))
    if searched_invoices == [] and request.method == 'POST':
        flash(f'No invoices found for your search', 'danger')
    return render_template('search.html', title='Search invoices', form=form, posts=searched_invoices)

