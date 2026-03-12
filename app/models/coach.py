from app.config.db import db
from datetime import datetime

class Coach(db.Model):
    __tablename__ = 'Coaches'
    coach_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False, unique=True)
    specialization = db.Column(db.Enum('fitness', 'nutrition', 'both'), default='fitness')
    certifications = db.Column(db.Text, nullable=True)
    experience_years = db.Column(db.Integer, nullable=True)
    gym = db.Column(db.String(100), nullable=True)
    cost = db.Column(db.Numeric(10, 2), nullable=False)
    hourly_rate = db.Column(db.Numeric(10, 2), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum('active', 'pending', 'approved', 'suspended', 'disabled', 'rejected'), nullable=False, default='active')
    verified_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='coach_profile')
    availability = db.relationship('CoachAvailability', backref='coach', lazy=True)

    def __repr__(self):
        return f'<Coach {self.user_id}>'
