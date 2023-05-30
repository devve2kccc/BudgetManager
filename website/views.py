from flask import Blueprint, jsonify, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Main, Bank
from . import db
from sqlalchemy import extract
from datetime import datetime, date, timedelta

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        transationname = request.form.get('transationname')
        addmoney = request.form.get('addmoney')
        date_str = request.form.get('date')
        category = request.form.get('category')
        custom_category = request.form.get('custom_category')

        if not date_str:
            flash('Date is required', category='error')
            return redirect(url_for('views.home'))

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format', category='error')
            return redirect(url_for('views.home'))

        if not addmoney:
            flash('Amount is required', category='error')
            return redirect(url_for('views.home'))

        if not category and not custom_category:
            flash('Category is required', category='error')
            return redirect(url_for('views.home'))

        selected_category = category if category else custom_category

        new_add = Main(
            transaction_name=transationname,
            amount=addmoney,
            transaction_type='expense',
            date=date,
            category=selected_category,
            user_id=current_user.id
        )
        db.session.add(new_add)
        db.session.commit()
        flash('Expense created successfully!', category='success')

    # Get all transactions for the current user (initial view)
    transactions = Main.query.filter_by(user_id=current_user.id).all()
    total_expense = sum(transaction.amount for transaction in transactions if transaction.transaction_type == 'expense')


    return render_template("home.html", user=current_user, transactions=transactions , total_expense=total_expense)

@views.route('/filter', methods=['POST'])
@login_required
def filter_transactions():
    filter_type = request.json.get('filter')
    start_date = request.json.get('start_date')
    end_date = request.json.get('end_date')

    # Get all transactions for the current user
    transactions = Main.query.filter_by(user_id=current_user.id)

    if filter_type == 'month':
        # Filter by month
        transactions = transactions.filter(extract('month', Main.date) == date.today().month)
    elif filter_type == 'week':
        # Filter by week
        start_of_week = date.today() - timedelta(days=date.today().weekday())
        end_of_week = start_of_week + timedelta(days=6)
        transactions = transactions.filter(Main.date.between(start_of_week, end_of_week))
    elif filter_type == 'day':
        # Filter by day
        transactions = transactions.filter(Main.date == date.today())
    elif filter_type == 'range' and start_date and end_date:
        # Filter by range of dates
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        transactions = transactions.filter(Main.date.between(start_date, end_date))

    # Execute the query and get the filtered transactions
    filtered_transactions = transactions.all()

    # Return the filtered transactions as JSON response
    return jsonify(transactions=[transaction.serialize() for transaction in filtered_transactions])


# apply here the same logic of the home route, but for banks, and make the request to database to get the values
@views.route('/banks', methods=['GET', 'POST'])
@login_required
def banks():
    # add bank information and balance to the database
    if request.method == 'POST':
        bankname = request.form.get('bankName')
        balance = request.form.get('bankBalance')
        if len(balance) < 1:
            flash('Ammout Error', category='error')
        else:
            new_add = Bank(bankname=bankname, ammout=balance,
                           user_id=current_user.id)
            db.session.add(new_add)
            db.session.commit()
            flash('Bank added', category='success')

    return render_template("banks.html", user=current_user)
