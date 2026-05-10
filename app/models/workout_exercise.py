from app.config.db import db
from datetime import datetime

class WorkoutExercise(db.Model):
    __tablename__ = 'workoutexercises'

    workout_exercises_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plan_id    = db.Column(db.Integer, db.ForeignKey('workoutplans.plan_id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.e_id'), nullable=False)
    num_sets   = db.Column(db.Integer, nullable=True)
    reps       = db.Column(db.Integer, nullable=True)
    num_length = db.Column(db.Integer, nullable=True)
    rest_time  = db.Column(db.Integer, nullable=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    notes      = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    plan     = db.relationship('WorkoutPlan', backref='exercises')
    exercise = db.relationship('Exercise', backref='workout_entries')

    def to_dict(self):
        return {
            'workout_exercises_id': self.workout_exercises_id,
            'plan_id':      self.plan_id,
            'exercise_id':  self.exercise_id,
            'exercise_name': self.exercise.name if self.exercise else None,
            'num_sets':     self.num_sets,
            'reps':         self.reps,
            'num_length':   self.num_length,
            'rest_time':    self.rest_time,
            'sort_order':   self.sort_order,
            'notes':        self.notes,
        }