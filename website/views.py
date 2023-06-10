from datetime import datetime, date, timedelta
from flask import Blueprint, jsonify, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import extract, func
from .models import Main, Bank, User, CashSources
from . import db

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        transaction_name = request.form.get('transactionname')
        amount = request.form.get('amount')
        date_str = request.form.get('date')
        category = request.form.get('category')
        custom_category = request.form.get('custom_category')
        transaction_type = request.form.get('transaction_type')
        payment_method = request.form.get('payment_method')
        bank_id = request.form.get('bank')
        cash_id = request.form.get('cash')
        selected_bank = None

        if bank_id:
            selected_bank = Bank.query.get(bank_id)
        
        if cash_id:
            selected_cash = CashSources.query.get(cash_id)

        if not date_str:
            flash('Date is required', category='error')
            return redirect(url_for('views.home'))

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format', category='error')
            return redirect(url_for('views.home'))

        if not amount:
            flash('Amount is required', category='error')
            return redirect(url_for('views.home'))

        if not category and not custom_category:
            flash('Category is required', category='error')
            return redirect(url_for('views.home'))

        selected_category = category if category else custom_category
        selected_bank = Bank.query.filter_by(id=request.form.get(
            'bank')).first() if payment_method == 'bank' else None
        
        selected_cash = CashSources.query.filter_by(id=request.form.get(
            'cash')).first() if payment_method == 'cash' else None

        new_add = Main(
            transaction_name=transaction_name,
            amount=amount,
            transaction_type=transaction_type,
            date=date,
            category=selected_category,
            user_id=current_user.id,
            payment_method=payment_method,
            bank_id=selected_bank.id if selected_bank else None,
            cash_id=selected_cash.id if selected_cash else None
        )

        if payment_method == 'bank' and bank_id and transaction_type == 'Expense':
            selected_bank = Bank.query.get(bank_id)
            if selected_bank:
                selected_bank.ammout -= float(amount)
                db.session.commit()
        elif payment_method == 'bank' and bank_id and transaction_type == 'Income':
            selected_bank = Bank.query.get(bank_id)
            if selected_bank:
                selected_bank.ammout += float(amount)
                db.session.commit()
        elif payment_method == 'cash' and bank_id and transaction_type == 'Expense':
            selected_cash = CashSources.query.get(cash_id)
            if selected_cash:
                selected_cash.balance -= float(amount)
                db.session.commit()
        elif payment_method == 'cash' and bank_id and transaction_type == 'Income':
            selected_cash = CashSources.query.get(bank_id)
            if selected_cash:
                selected_cash.balance += float(amount)
                db.session.commit()

        db.session.add(new_add)
        db.session.commit()

        if transaction_type == 'Expense':
            flash('Expense created successfully!', category='success')
        elif transaction_type == 'Income':
            flash('Income added successfully!', category='success')

        return redirect(url_for('views.home'))
    # Get all transactions for the current user (initial view)
    transactions = Main.query.filter_by(user_id=current_user.id).all()
    total_expenses = sum(
        transaction.amount for transaction in transactions if transaction.transaction_type == 'Expense')
    total_income = sum(
        transaction.amount for transaction in transactions if transaction.transaction_type == 'Income')
    banks = Bank.query.filter_by(user_id=current_user.id).all()
    cash_sources = CashSources.query.filter_by(user_id=current_user.id).all()
    user = User.query.get(current_user.id)
    total_money = user.total_money
    

    return render_template("home.html", user=current_user, transactions=transactions, total_expenses=total_expenses, total_income=total_income, banks=banks, total_money=total_money, cash_sources=cash_sources)


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
        transactions = transactions.filter(
            extract('month', Main.date) == date.today().month)
    elif filter_type == 'week':
        # Filter by week
        start_of_week = date.today() - timedelta(days=date.today().weekday())
        end_of_week = start_of_week + timedelta(days=6)
        transactions = transactions.filter(
            Main.date.between(start_of_week, end_of_week))
    elif filter_type == 'day':
        # Filter by day
        transactions = transactions.filter(Main.date == date.today())
    elif filter_type == 'range' and start_date and end_date:
        # Filter by range of dates
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        transactions = transactions.filter(
            Main.date.between(start_date, end_date))

    # Execute the query and get the filtered transactions
    filtered_transactions = transactions.all()

    # Return the filtered transactions as JSON response
    return jsonify(transactions=[transaction.serialize() for transaction in filtered_transactions])


@views.route('/delete/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Main.query.get(transaction_id)
    if transaction:
        if transaction.user_id == current_user.id:
            if transaction.transaction_type == 'Expense':
                # Adding money back to the bank or cash
                if transaction.payment_method == 'bank':
                    bank = Bank.query.get(transaction.bank_id)
                    if bank:
                        bank.ammout += transaction.amount
                        db.session.commit()
                elif transaction.payment_method == 'cash':
                    user = User.query.get(current_user.id)
                    if user:
                        user.cash = (user.cash or 0) + transaction.amount
                        db.session.commit()

            elif transaction.transaction_type == 'Income':
                # Subtracting money from the bank or cash
                if transaction.payment_method == 'bank':
                    bank = Bank.query.get(transaction.bank_id)
                    if bank:
                        bank.ammout -= transaction.amount
                        db.session.commit()
                elif transaction.payment_method == 'cash':
                    user = User.query.get(current_user.id)
                    if user:
                        user.cash = (user.cash or 0) - transaction.amount
                        db.session.commit()

            db.session.delete(transaction)
            db.session.commit()
            return jsonify({"message": "Transaction deleted successfully."})

    return jsonify({"message": "Failed to delete the transaction."}), 400

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


@views.route('/cash', methods=['GET', 'POST'])
@login_required
def cash():
    # add bank information and balance to the database
    if request.method == 'POST':
        cashsource = request.form.get('cashSource')
        balance = request.form.get('cashBalance')
        if len(balance) < 1:
            flash('Ammout Error', category='error')
        else:
            new_add = CashSources(cashname=cashsource, balance=balance,
                           user_id=current_user.id)
            db.session.add(new_add)
            db.session.commit()
            flash('Cash added', category='success')

    return render_template("banks.html", user=current_user)


@views.route('/banks/<int:bank_id>', methods=['POST'])
@login_required
def delete_bank(bank_id):
    bank = Bank.query.get(bank_id)
    if bank:
        if bank.user_id == current_user.id:
            db.session.delete(bank)
            db.session.commit()
            return jsonify({"message": "Bank deleted successfully."})

    return jsonify({"message": "Failed to delete the bank."}), 400


@views.route('/api/chart-data')
@login_required
def chart_data():
    # Retrieve the banks and their balances for the current user
    user_banks = Bank.query.filter_by(user_id=current_user.id).all()
    bank_names = [bank.bankname for bank in user_banks]
    bank_balances = [bank.ammout for bank in user_banks]

    # Calculate the total balance
    total_balance = sum(bank_balances)

    # Prepare the data for the chart
    chart_data = {
        'labels': bank_names,
        'datasets': [
            {
                'data': bank_balances,
                # Customize the colors as desired
                'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56', '#8A2BE2', '#3CB371', '#BA55D3', '#FF4500', '#9932CC', '#FFA500', '#00CED1']
            }
        ],
        'total_balance': total_balance
    }

    return jsonify(chart_data)


@views.route('/api/total-money')
@login_required
def total_money_data():
    user = User.query.get(current_user.id)
    cash_total = db.session.query(
        func.sum(CashSources.balance)).filter_by(user_id=user.id).scalar()
    bank_total = sum([bank.ammout for bank in user.banks])
    total_money = user.total_money

    data = {
        'cash': cash_total,
        'bankTotal': bank_total,
        'totalMoney': total_money
    }

    return jsonify(data)
