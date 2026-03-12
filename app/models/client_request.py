from app.config.db import db
from datetime import datetime

class ClientRequest(db.Model):
    __tablename__ = 'ClientRequests'
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('Coaches.coach_id'), nullable=False)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum('pending', 'accepted', 'declined'), nullable=False, default='pending')
    responded_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = db.relationship('User', backref='client_requests')
    coach = db.relationship('Coach', backref='client_requests')

    def __repr__(self):
        return f'<ClientRequest {self.client_id} -> {self.coach_id}>'
