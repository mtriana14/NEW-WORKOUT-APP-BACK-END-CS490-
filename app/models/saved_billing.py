from app.config.db import db
from datetime import datetime

class SavedBilling(db.Model):
    __tablename__ = 'savedbilling'
    card_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    last_four = db.Column(db.String(4), nullable=False)
    card_brand = db.Column(db.String(20), nullable=True)
    expiry_month = db.Column(db.Integer, nullable=False)
    expiry_year = db.Column(db.Integer, nullable=False)
    is_default = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='saved_billing')

    def __repr__(self):
        return f'<SavedBilling {self.card_id} - {self.last_four}>'
