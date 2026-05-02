from app.config.db import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('Coaches.coach_id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('Subscriptions.subscription_id'), nullable=True)
    card_id = db.Column(db.Integer, db.ForeignKey('SavedBilling.card_id'), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(10), nullable=False, default='USD')
    payment_method_type = db.Column(db.Enum('credit_card', 'debit_card', 'paypal'), nullable=True)
    status = db.Column(db.Enum('pending', 'completed', 'failed', 'refunded'), nullable=False, default='pending')
    transaction_id = db.Column(db.String(255), unique=True, nullable=True)
    description = db.Column(db.String(255), nullable=True)
    paid_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = db.relationship('User', backref='payments')
    coach = db.relationship('Coach', backref='payments')

    def __repr__(self):
        return f'<Payment {self.transaction_id} - {self.status}>'
