from operator import le
from unicodedata import category
from flask import Blueprint, jsonify, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Main
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
            flash('Ammout Error', category='error')
        else:
            new_add = Main(ammout=addmoney, transationname=transationname, type='ADD',  user_id=current_user.id)
            db.session.add(new_add)
            db.session.commit()
            flash('Money added', category='success') 

    
      # sum all values on the table
    sum = db.session.query(db.func.sum(Main.ammout)).filter_by(user_id=current_user.id).scalar()
    return render_template("home.html", user=current_user, sum=sum)
