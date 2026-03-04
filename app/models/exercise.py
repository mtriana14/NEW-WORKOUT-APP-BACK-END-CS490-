from app.config.db import db
from datetime import datetime

class Exercise(db.Model):
    """Exercise model - master database of exercises managed by admin."""
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    muscle_group = db.Column(db.Enum(
        'chest', 'back', 'shoulders', 'arms',
        'legs', 'glutes', 'core', 'full_body'
    ), nullable=False)
    equipment = db.Column(db.Enum(
        'barbell', 'dumbbell', 'machine',
        'bodyweight', 'cables', 'bands', 'other'
    ), nullable=False, default='bodyweight')
    difficulty = db.Column(db.Enum('beginner', 'intermediate', 'advanced'), nullable=False, default='beginner')
    instructions = db.Column(db.Text, nullable=True)
    video_url = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    admin = db.relationship('User', backref='exercises')

    def __repr__(self):
        return f'<Exercise {self.name}>'