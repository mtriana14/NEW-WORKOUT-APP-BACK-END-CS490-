from app.config.db import db
from datetime import datetime

class Subscription(db.Model):
    __tablename__ = 'Subscriptions'
    subscription_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('Coaches.coach_id'), nullable=False)
    plan_type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('active', 'cancelled', 'paused', 'expired'), nullable=False, default='active')
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    next_billing = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='subscriptions')
    coach = db.relationship('Coach', backref='subscriptions')

    def __repr__(self):
        return f'<Subscription {self.subscription_id} - {self.status}>'
