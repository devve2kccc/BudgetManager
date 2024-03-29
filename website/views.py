from datetime import datetime, date, timedelta
from flask import Blueprint, jsonify, render_template, request, flash, redirect, url_for, send_file, abort
from flask_login import login_required, current_user
import requests
from sqlalchemy import extract, func
from .models import Main, Bank, User, CashSources, GeneratedReport, Saving, Crypto
from . import db
import os
import pdfkit
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        transaction_name = request.form.get('transactionname')
        amount = request.form.get('currency-field')
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
        
        amount = amount.replace('$', '').replace(',', '')

        
        try:
            amount = float(amount)
        except ValueError:
            flash('Invalid amount format', category='error')
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
        elif payment_method == 'cash' and cash_id and transaction_type == 'Expense':
            selected_cash = CashSources.query.get(cash_id)
            if selected_cash:
                selected_cash.balance -= float(amount)
                db.session.commit()
        elif payment_method == 'cash' and cash_id and transaction_type == 'Income':
            selected_cash = CashSources.query.get(cash_id)
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
                    cash = CashSources.query.get(current_user.id)
                    if cash:
                        cash.balance = (cash.balance or 0) + transaction.amount
                        db.session.commit()

            elif transaction.transaction_type == 'Income':
                # Subtracting money from the bank or cash
                if transaction.payment_method == 'bank':
                    bank = Bank.query.get(transaction.bank_id)
                    if bank:
                        bank.ammout -= transaction.amount
                        db.session.commit()
                elif transaction.payment_method == 'cash':
                    cash = CashSources.query.get(current_user.id)
                    if cash:
                        cash.balance = (cash.balance or 0) - transaction.amount
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
        redirect(url_for('views.banks'))

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
        redirect(url_for('views.cash'))

    return render_template("banks.html", user=current_user)

@views.route('/update_cash/<int:cash_id>', methods=['POST'])
def update_cash(cash_id):
    cash = CashSources.query.get(cash_id)

    if not cash:
        return jsonify({'error': 'Cash not found'})

    action = request.form.get('action')

    if action == 'subtract':
        updated_amount_str = request.form.get('add-cash-amount')
        if updated_amount_str:
            try:
                updated_amount = float(updated_amount_str)
                cash.balance -= updated_amount
                db.session.commit()
                return redirect(url_for('views.cash'))  # Redirect to the appropriate page after subtracting
            except ValueError:
                return jsonify({'error': 'Invalid amount'})

    elif action == 'add':
        updated_amount_str = request.form.get('add-cash-amount')
        if updated_amount_str:
            try:
                updated_amount = float(updated_amount_str)
                cash.balance += updated_amount
                db.session.commit()
                return redirect(url_for('views.cash'))  # Redirect to the appropriate page after adding
            except ValueError:
                return jsonify({'error': 'Invalid amount'})

    return jsonify({'error': 'Invalid action'})

@views.route('/cashs/<int:cash_id>', methods=['POST'])
@login_required
def delete_cash(cash_id):
    cash = CashSources.query.get(cash_id)
    if cash:
        if cash.user_id == current_user.id:
            db.session.delete(cash)
            db.session.commit()
            return jsonify({"message": "Cash deleted successfully."})

    return jsonify({"message": "Failed to delete the Cash."}), 400



@views.route('/update_bank/<int:bank_id>', methods=['POST'])
def update_bank(bank_id):
    bank = Bank.query.get(bank_id)

    if not bank:
        return jsonify({'error': 'Bank not found'})

    action = request.form.get('action')

    if action == 'subtract':
        updated_amount_str = request.form.get('add-bank-amount')
        if updated_amount_str:
            try:
                updated_amount = float(updated_amount_str)
                bank.ammout -= updated_amount
                db.session.commit()
                return redirect(url_for('views.banks'))  # Redirect to the appropriate page after subtracting
            except ValueError:
                return jsonify({'error': 'Invalid amount'})

    elif action == 'add':
        updated_amount_str = request.form.get('add-bank-amount')
        if updated_amount_str:
            try:
                updated_amount = float(updated_amount_str)
                bank.ammout += updated_amount
                db.session.commit()
                return redirect(url_for('views.banks'))  # Redirect to the appropriate page after adding
            except ValueError:
                return jsonify({'error': 'Invalid amount'})

    return jsonify({'error': 'Invalid action'})



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

@views.route('/addsafe', methods=['GET', 'POST'])
@login_required
def addsafe():
    # add bank information and balance to the database
    if request.method == 'POST':
        safename = request.form.get('safeName')
        balance = request.form.get('safeBalance')
        if len(balance) < 1:
            flash('Balance Error', category='error')
        else:
            new_add = Saving(safename=safename, balance=balance,
                           user_id=current_user.id)
            db.session.add(new_add)
            db.session.commit()
            flash('Safe added', category='success')
        return redirect(url_for('views.addsafe')) 

    return render_template("savings.html", user=current_user)

@views.route('/savings/<int:safe_id>', methods=['POST'])
@login_required
def delete_safe(safe_id):
    safe = Saving.query.get(safe_id)
    if safe:
        if safe.user_id == current_user.id:
            db.session.delete(safe)
            db.session.commit()
            return jsonify({"message": "Safe deleted successfully."})

    return jsonify({"message": "Failed to delete the Safe."}), 400


@views.route('/update_safe/<int:safe_id>', methods=['POST'])
def update_safe(safe_id):
    safe = Saving.query.get_or_404(safe_id)

    action = request.form.get('action')

    if action == 'subtract':
        updated_amount_str = request.form.get('add-safe-amount')
        if updated_amount_str:
            try:
                updated_amount = float(updated_amount_str)
                safe.balance -= updated_amount
                db.session.commit()
                flash('Safe balance updated successfully', 'success')
                return redirect(url_for('views.addsafe'))
            except ValueError:
                flash('Invalid amount', 'error')

    elif action == 'add':
        updated_amount_str = request.form.get('add-safe-amount')
        if updated_amount_str:
            try:
                updated_amount = float(updated_amount_str)
                safe.balance += updated_amount
                db.session.commit()
                flash('Safe balance updated successfully', 'success')
                return redirect(url_for('views.addsafe'))
            except ValueError:
                flash('Invalid amount', 'error')

    return redirect(url_for('views.addsafe'))


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

@views.route('/profile', methods=['GET'])
@login_required
def profile():
        # Fetch the oldest and latest transaction dates
    oldest_transaction = Main.query.filter_by(user_id=current_user.id).order_by(Main.date.asc()).first()
    latest_transaction = Main.query.filter_by(user_id=current_user.id).order_by(Main.date.desc()).first()

    # Convert the dates to the expected format (YYYY-MM-DD)
    min_date = oldest_transaction.date.strftime('%Y-%m-%d') if oldest_transaction else ''
    max_date = latest_transaction.date.strftime('%Y-%m-%d') if latest_transaction else ''
    generated_reports = GeneratedReport.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', user=current_user, generated_reports=generated_reports, min_date=min_date, max_date=max_date)


@views.route('/generate_pdf', methods=['POST'])
@login_required
def generate_pdf():
    # Get the selected timeframe from the form
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    # Query the database for transactions within the selected timeframe for the current user
    transactions = Main.query.filter(
        Main.user_id == current_user.id,
        Main.date >= start_date,
        Main.date <= end_date
    ).all()

    # Calculate total money, expenses, and income for the selected timeframe
    total_money = current_user.total_money
    total_expenses = sum(
        transaction.amount for transaction in transactions if transaction.transaction_type == 'Expense'
    )
    total_income = sum(
        transaction.amount for transaction in transactions if transaction.transaction_type == 'Income'
    )

    # Render the report template with the fetched data
    rendered_template = render_template(
        'report.html',
        transactions=transactions,
        total_money=total_money,
        total_expenses=total_expenses,
        total_income=total_income
    )

    # Define the path for the user's folder (change the path as per your project structure)
    user_folder = os.path.join(os.getcwd(), 'pdf_reports', str(current_user.id))

    # Create the user's folder if it doesn't exist
    os.makedirs(user_folder, exist_ok=True)

    # Generate a unique filename for the PDF report
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = os.path.join(user_folder, f"report_{timestamp}.pdf")

    # Generate PDF using pdfkit and save it in the user's folder
    pdfkit.from_string(rendered_template, filename)
    
    generated_report = GeneratedReport(user_id=current_user.id, filename=filename)
    db.session.add(generated_report)
    db.session.commit()

    # Send the PDF file as a response for download
    return send_file(filename, as_attachment=True)


@views.route('/download_report/<int:report_id>')
@login_required
def download_report(report_id):
    # Query the database for the specified generated report
    report = GeneratedReport.query.get(report_id)

    if report is None or report.user_id != current_user.id:
        # If the report doesn't exist or doesn't belong to the current user, return a 404 error
        abort(404)

    # Send the report file as a response for download
    return send_file(report.filename, as_attachment=True)


@views.route('/api/cryptos', methods=['GET'])
def get_cryptos():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit': '5000',
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': '743673aa-1539-4837-9a91-84e3fd75b9d2'  # Replace with your own API key
    }

    try:
        response = requests.get(url, params=parameters, headers=headers)
        data = response.json()

        # Calculate the total investment for each cryptocurrency
        for crypto in data['data']:
            crypto_id = crypto['id']
            crypto_obj = Crypto.query.filter_by(crypto_id=crypto_id, user_id=current_user.id).first()
            if crypto_obj:
                crypto['total_investment'] = crypto['quote']['USD']['price'] * crypto_obj.amount
            else:
                crypto['total_investment'] = 0

        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)})


@views.route('/crypto', methods=['GET'])
@login_required
def crypto():
    cryptos = Crypto.query.filter_by(user_id=current_user.id).all()
    crypto_data = []

    for crypto in cryptos:
        crypto_id = crypto.crypto_id
        crypto_name = crypto.crypto_name

        # Fetch the current price of the crypto using the CoinMarketCap API
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        parameters = {
            'id': crypto_id,
            'convert': 'USD'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': '743673aa-1539-4837-9a91-84e3fd75b9d2'  # Replace with your own API key
        }

        try:
            response = requests.get(url, params=parameters, headers=headers)
            data = response.json()

            if 'data' in data:
                crypto_data.append({
                    'id': crypto.id,  # This is the ID of the crypto in the database, not the 'id' from the API response
                    'crypto_id': crypto_id,
                    'crypto_name': crypto_name,
                    'amount': crypto.amount,
                    'current_price': round(data['data'][str(crypto_id)]['quote']['USD']['price'], 2),
                    'total_investment': round(crypto.amount * data['data'][str(crypto_id)]['quote']['USD']['price'], 2)
                })
        except requests.exceptions.RequestException as e:
            print('Error:', str(e))

    return render_template('crypto.html', user=current_user, cryptos=crypto_data)

   

@views.route('/addcrypto', methods=['GET', 'POST'])
@login_required
def add_crypto():
    if request.method == 'POST':
        crypto_id = request.form.get('cryptoId')
        crypto_name = request.form.get('cryptoName')
        amount = request.form.get('cryptoBalance')
        
        if not amount:
            flash('Balance is required', category='error')
        else:
            try:
                amount = float(amount)
            except ValueError:
                flash('Invalid balance', category='error')
            else:
                new_crypto = Crypto(crypto_id=crypto_id, crypto_name=crypto_name, amount=amount, user_id=current_user.id)
                db.session.add(new_crypto)
                db.session.commit()
                flash('Crypto added', category='success')
        
        return redirect(url_for('views.crypto'))

    return render_template("crypto.html", user=current_user)


@views.route('/update_crypto/<int:crypto_id>', methods=['POST'])
def update_crypto(crypto_id):
    crypto = Crypto.query.get_or_404(crypto_id)

    action = request.form.get('action')

    if action == 'subtract':
        updated_amount_str = request.form.get('add-crypto-amount')
        if updated_amount_str:
            try:
                updated_amount = float(updated_amount_str)
                crypto.amount -= updated_amount
                db.session.commit()
                flash('Crypto holding updated successfully', 'success')
                return redirect(url_for('views.crypto'))
            except ValueError:
                flash('Invalid amount', 'error')

    elif action == 'add':
        updated_amount_str = request.form.get('add-crypto-amount')
        if updated_amount_str:
            try:
                updated_amount = float(updated_amount_str)
                crypto.amount += updated_amount
                db.session.commit()
                flash('Crypto holding updated successfully', 'success')
                return redirect(url_for('views.crypto'))
            except ValueError:
                flash('Invalid amount', 'error')

    return redirect(url_for('views.crypto'))



@views.route('/crypto/<int:crypto_id>', methods=['POST'])
@login_required
def delete_crypto(crypto_id):
    crypto = Crypto.query.get(crypto_id)

    if crypto and crypto.user_id == current_user.id:
        db.session.delete(crypto)
        db.session.commit()
        return jsonify({"message": "Crypto deleted successfully."})

    return jsonify({"message": "Failed to delete the crypto."}), 400