from app.config.db import db
from datetime import datetime

class Coach(db.Model):
    """Coach model - extends user with professional details."""
    __tablename__ = 'coaches'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    bio = db.Column(db.Text, nullable=True)
    specialization = db.Column(db.Enum('fitness', 'nutrition', 'both'), nullable=False, default='fitness')
    experience_years = db.Column(db.Integer, nullable=True)
    certifications = db.Column(db.Text, nullable=True)
    hourly_rate = db.Column(db.Numeric(10, 2), nullable=True)
    status = db.Column(db.Enum('pending', 'approved', 'suspended', 'rejected'), nullable=False, default='pending')
    verified_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='coach_profile')
    availability = db.relationship('CoachAvailability', backref='coach', lazy=True)

    def __repr__(self):
        return f'<Coach {self.user_id}>'