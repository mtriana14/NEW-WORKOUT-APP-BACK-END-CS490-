from app.config.db import db
from datetime import datetime

class CoachAvailability(db.Model):
    """Coach availability model - stores coach weekly schedule."""
    __tablename__ = 'coach_availability'

    id = db.Column(db.Integer, primary_key=True)
    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.id'), nullable=False)
    day_of_week = db.Column(db.Enum(
        'monday', 'tuesday', 'wednesday',
        'thursday', 'friday', 'saturday', 'sunday'
    ), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<CoachAvailability {self.coach_id} {self.day_of_week}>'