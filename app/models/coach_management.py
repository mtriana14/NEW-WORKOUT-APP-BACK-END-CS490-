from app.config.db import db
from datetime import datetime

class CoachManagement(db.Model):
    __tablename__ = 'CoachManagement'
    action_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    coach_id = db.Column(db.Integer, db.ForeignKey('Coaches.coach_id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    action_type = db.Column(db.Enum('suspend', 'reactivate', 'disable'), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    suspension_duration = db.Column(db.String(50), nullable=True)
    action_date = db.Column(db.DateTime, default=datetime.utcnow)

    coach = db.relationship('Coach', backref='management_actions')
    admin = db.relationship('User', backref='coach_management_actions')

    def __repr__(self):
        return f'<CoachManagement {self.coach_id} - {self.action_type}>'
