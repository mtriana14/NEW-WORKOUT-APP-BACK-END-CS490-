from app.config.db import db
from datetime import datetime

class CoachAvailability(db.Model):
    __tablename__ = 'CoachAvailability'
    availability_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    coach_id = db.Column(db.Integer, db.ForeignKey('Coaches.coach_id'), nullable=False)
    day_of_week = db.Column(db.Enum(
        'Monday', 'Tuesday', 'Wednesday',
        'Thursday', 'Friday', 'Saturday', 'Sunday'
    ), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<CoachAvailability {self.coach_id} {self.day_of_week}>'
