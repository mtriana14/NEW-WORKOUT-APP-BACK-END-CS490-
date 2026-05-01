from app.config.db import db
from datetime import datetime

class ProgressEntry(db.Model):
    __tablename__ = 'progress_entries'

    entry_id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id              = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    entry_date           = db.Column(db.Date, nullable=False)
    weight               = db.Column(db.Numeric(6, 2), nullable=True)
    workouts_completed   = db.Column(db.Integer, nullable=False, default=0)
    calories_burned      = db.Column(db.Integer, nullable=False, default=0)
    goal_completed       = db.Column(db.Boolean, nullable=False, default=False)
    notes                = db.Column(db.Text, nullable=True)
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at           = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='progress_entries')

    def to_dict(self):
        return {
            'entry_id':           self.entry_id,
            'user_id':            self.user_id,
            'entry_date':         self.entry_date.isoformat() if self.entry_date else None,
            'weight':             float(self.weight) if self.weight else None,
            'workouts_completed': self.workouts_completed,
            'calories_burned':    self.calories_burned,
            'goal_completed':     self.goal_completed,
            'notes':              self.notes,
            'created_at':         self.created_at.isoformat() if self.created_at else None,
            'updated_at':         self.updated_at.isoformat() if self.updated_at else None,
        }