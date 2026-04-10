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
    
    def to_dict(self):
        return {
            'coach_id': self.coach_id,
            'user_id': self.user_id,
            'specialization': self.specialization,
            'certifications': self.certifications,
            'experience_years': self.experience_years,
            'gym': self.gym,
            'cost': str(self.cost),
            'hourly_rate': str(self.hourly_rate) if self.hourly_rate else None,
            'bio': self.bio,
            'status': self.status,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
