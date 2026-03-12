from app.config.db import db
from datetime import datetime

class CoachRegistration(db.Model):
    __tablename__ = 'CoachRegistrations'
    reg_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False, unique=True)
    qualifications = db.Column(db.Text, nullable=True)
    specialty = db.Column(db.Text, nullable=True)
    document_links = db.Column(db.String(500), nullable=True)
    application_status = db.Column(db.Enum('pending', 'approved', 'rejected'), nullable=False, default='pending')
    rejection_reason = db.Column(db.Text, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applicant = db.relationship('User', foreign_keys=[user_id], backref='coach_registration')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='reviewed_registrations')

    def __repr__(self):
        return f'<CoachRegistration {self.user_id} - {self.application_status}>'
