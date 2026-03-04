from app.config.db import db
from datetime import datetime

class User(db.Model):
    """User model - base for coaches, clients and admins."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=True)  # Nullable for OAuth users
    role = db.Column(db.Enum('client', 'coach', 'admin'), nullable=False, default='client')
    profile_photo = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    oauth_provider = db.Column(db.String(50), nullable=True)  # google, etc
    oauth_id = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.email}>'