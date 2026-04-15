from app.config.db import db
from datetime import datetime

class Exercise(db.Model):
    __tablename__ = 'Exercises'
    e_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    equipment_type = db.Column(db.Enum(
        'barbell', 'dumbbell', 'machine',
        'bodyweight', 'cables', 'bands', 'other'
    ), default='bodyweight')
    muscle_group = db.Column(db.Enum(
        'chest', 'back', 'shoulders', 'arms',
        'legs', 'glutes', 'core', 'full_body'
    ), nullable=True)
    difficulty = db.Column(db.Enum('beginner', 'intermediate', 'advanced'), default='beginner')
    instructions = db.Column(db.Text, nullable=True)
    video_url = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    admin = db.relationship('User', backref='exercises')

    def __repr__(self):
        return f'<Exercise {self.name}>'
