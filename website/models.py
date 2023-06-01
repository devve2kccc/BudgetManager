from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Float
from sqlalchemy.orm import object_session
from sqlalchemy import event


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
    transaction_id = db.Column(db.Integer)  # Unique transaction ID
    transaction_name = db.Column(db.String(10000))
    # Add transaction_type column
    transaction_type = db.Column(db.String(10000))
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date)
    category = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    payment_method = db.Column(db.String(20))
    bank_id = db.Column(db.Integer, db.ForeignKey('bank.id'))

    user_relation = db.relationship('User', backref=db.backref('transactions', lazy=True))
    bank = db.relationship('Bank', backref=db.backref('transactions', lazy=True))

    @staticmethod
    def generate_transaction_id(mapper, connection, target):
        session = object_session(target)
        max_transaction_id = session.query(func.max(Main.transaction_id)).filter_by(user_id=target.user_id).scalar()

        if max_transaction_id is not None:
            target.transaction_id = max_transaction_id + 1
        else:
            target.transaction_id = 1
    
    def serialize(self):
        return {
            'transaction_id': self.id,
            'transaction_name': self.transaction_name,
            'amount': self.amount,
            'category': self.category,
            'date': self.date.strftime('%Y-%m-%d'),
            'transaction_type': self.transaction_type
        }

# Associate the event listener to generate transaction ID
event.listen(Main, 'before_insert', Main.generate_transaction_id)

class Bank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bankname = db.Column(db.String(10000), nullable=False)
    ammout = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
