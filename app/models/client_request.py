from app.config.db import db
from datetime import datetime

class ClientRequest(db.Model):
    """Client request model - stores coaching requests from clients to coaches."""
    __tablename__ = 'client_requests'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.id'), nullable=False)
    status = db.Column(db.Enum('pending', 'accepted', 'declined'), nullable=False, default='pending')
    message = db.Column(db.Text, nullable=True)  # Optional message from client
    responded_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    client = db.relationship('User', backref='client_requests')
    coach = db.relationship('Coach', backref='client_requests')

    def __repr__(self):
        return f'<ClientRequest {self.client_id} -> {self.coach_id}>'