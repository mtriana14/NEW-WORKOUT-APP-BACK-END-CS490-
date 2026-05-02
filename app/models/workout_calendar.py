from app.config.db import db
from datetime import datetime

class WorkoutCalendar(db.Model):
    __tablename__ = 'workoutcalendar'

    calendar_id    = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    plan_id        = db.Column(db.Integer, db.ForeignKey('workoutplans.plan_id'), nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False)
    is_completed   = db.Column(db.Boolean, nullable=False, default=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='workout_calendar')
    plan = db.relationship('WorkoutPlan', backref='calendar_entries')

    def to_dict(self):
        return {
            'calendar_id':    self.calendar_id,
            'user_id':        self.user_id,
            'plan_id':        self.plan_id,
            'plan_name':      self.plan.name if self.plan else None,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'is_completed':   self.is_completed,
            'created_at':     self.created_at.isoformat() if self.created_at else None,
        }