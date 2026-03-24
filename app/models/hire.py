from app.config.db import db
from datetime import datetime

class Hire(db.Model):
    __tablename__ = 'Hires'
    hire_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('Coaches.coach_id'), nullable=False)
    status = db.Column(db.Enum('active', 'completed', 'cancelled'), nullable=False, default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='hires')
    coach = db.relationship('Coach', backref='hires')

    def __repr__(self):
        return f'<Hire {self.user_id} -> {self.coach_id}>'