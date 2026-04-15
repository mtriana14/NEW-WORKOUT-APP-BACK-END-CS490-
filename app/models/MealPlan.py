from app.config.db import db
from datetime import datetime


class MealPlan(db.Model):
    __tablename__ = 'mealplans'
    
    meal_plan_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('Coaches.coach_id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum('active', 'inactive', 'completed'), nullable=False, default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='meal_plans')
    coach = db.relationship('Coach', backref='meal_plans')

    def __repr__(self):
        return f'<MealPlan {self.meal_plan_id} - {self.name}>'