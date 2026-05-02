from app.config.db import db
from datetime import datetime


class WorkoutPlan(db.Model):
    __tablename__ = 'workoutplans'
    
    plan_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.coach_id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum('active', 'inactive', 'completed'), nullable=False, default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='workout_plans')
    coach = db.relationship('Coach', backref='workout_plans')

    def __repr__(self):
        return f'<WorkoutPlan {self.plan_id} - {self.name}>'