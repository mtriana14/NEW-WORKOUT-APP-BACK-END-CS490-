from app.config.db import db
from datetime import datetime

class ActivityLog(db.Model):
    __tablename__ = 'activitylogs'

    log_id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    activity_type    = db.Column(db.Enum('strength', 'cardio', 'steps', 'calories'), nullable=False)
    # Strength fields
    exercise_id      = db.Column(db.Integer, db.ForeignKey('exercises.e_id'), nullable=True)
    sets_completed   = db.Column(db.Integer, nullable=True)
    reps_completed   = db.Column(db.Integer, nullable=True)
    weight_used      = db.Column(db.Numeric(6, 2), nullable=True)
    # Cardio fields
    distance         = db.Column(db.Numeric(8, 2), nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True)
    cardio_type      = db.Column(db.String(100), nullable=True)
    # Steps / calories fields
    step_count       = db.Column(db.Integer, nullable=True)
    calorie_intake   = db.Column(db.Integer, nullable=True)
    # Common
    log_date         = db.Column(db.Date, nullable=False)
    notes            = db.Column(db.Text, nullable=True)
    is_deleted       = db.Column(db.Boolean, nullable=False, default=False)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at       = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user     = db.relationship('User', backref='activity_logs')
    exercise = db.relationship('Exercise', backref='activity_logs')

    def to_dict(self):
        return {
            'log_id':           self.log_id,
            'user_id':          self.user_id,
            'activity_type':    self.activity_type,
            'exercise_id':      self.exercise_id,
            'sets_completed':   self.sets_completed,
            'reps_completed':   self.reps_completed,
            'weight_used':      float(self.weight_used) if self.weight_used else None,
            'distance':         float(self.distance) if self.distance else None,
            'duration_minutes': self.duration_minutes,
            'cardio_type':      self.cardio_type,
            'step_count':       self.step_count,
            'calorie_intake':   self.calorie_intake,
            'log_date':         self.log_date.isoformat() if self.log_date else None,
            'notes':            self.notes,
            'created_at':       self.created_at.isoformat() if self.created_at else None,
        }