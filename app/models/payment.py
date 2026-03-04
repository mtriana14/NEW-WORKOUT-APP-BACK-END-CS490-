from app.config.db import db
from datetime import datetime

class Payment(db.Model):
    """Payment model - stores all payment transactions for admin dashboard."""
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(10), nullable=False, default='USD')
    status = db.Column(db.Enum('pending', 'completed', 'failed', 'refunded'), nullable=False, default='pending')
    payment_method = db.Column(db.Enum('credit_card', 'debit_card', 'paypal'), nullable=False)
    transaction_id = db.Column(db.String(255), unique=True, nullable=True)  # External payment gateway ID
    description = db.Column(db.String(255), nullable=True)
    paid_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    client = db.relationship('User', backref='payments')
    coach = db.relationship('Coach', backref='payments')

    def __repr__(self):
        return f'<Payment {self.transaction_id} - {self.status}>'