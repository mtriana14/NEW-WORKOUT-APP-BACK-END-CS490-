from app.config.db import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=True)
    role = db.Column(db.Enum('client', 'coach', 'admin'), nullable=False, default='client')
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    weight = db.Column(db.Numeric(5, 2), nullable=True)
    height = db.Column(db.Numeric(5, 2), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    profile_photo = db.Column(db.String(255), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.Enum('male', 'female', 'other', 'prefer_not_to_say'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.email}>'
