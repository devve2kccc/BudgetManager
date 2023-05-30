from operator import le
from unicodedata import category
from flask import Blueprint, jsonify, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Main, Bank
from . import db
import random
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        transationname = request.form.get('transationname')
        addmoney = request.form.get('addmoney')
        if len(addmoney) < 1:
            flash('Amount Error', category='error')
        else:
            new_add = Main(amount=addmoney, transaction_name=transationname, transaction_type='ADD',  user_id=current_user.id)
            db.session.add(new_add)
            db.session.commit()
            flash('Money added', category='success') 

    
      # sum all values on the table
    sum = db.session.query(db.func.sum(Main.amount)).filter_by(user_id=current_user.id).scalar()
    return render_template("home.html", user=current_user, sum=sum)


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
            new_add = Bank(bankname=bankname, ammout=balance, user_id=current_user.id)
            db.session.add(new_add)
            db.session.commit()
            flash('Bank added', category='success')

    return render_template("banks.html", user=current_user)
