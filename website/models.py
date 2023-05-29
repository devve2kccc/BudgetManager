from . import db  
from flask_login import UserMixin 
from sqlalchemy.sql import func
from sqlalchemy import Float


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))

    #  um urilizador pode ter muitas transações
    mains = db.relationship('Main', backref='user')

    # um utilizador pode ter muitos bancos
    banks = db.relationship('Bank', backref='user')

class Main(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transationname = db.Column(db.String(10000))
    type = db.Column(db.String(10000))
    ammout = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Bank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bankname = db.Column(db.String(10000))
    ammout = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))