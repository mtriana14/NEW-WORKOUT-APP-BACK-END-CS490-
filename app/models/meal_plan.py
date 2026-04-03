from app.config.db import db
from datetime import datetime

class MealPlan(db.Model):
    __tablename__ = "mealplans"

    meal_plan_id = db.Column(db.Integer, primary_key = True, nullable=False, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id') ,nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('Coaches.coach_id') ,nullable=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Enum('active', 'achieved'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='mealplans')
    coach = db.relationship('Coach', backref='mealplans')

    def __repr__(self):
        return f'Mealplan for {self.user_id} : {self.description}'
    
    def to_dict(self):
        return {
            'meal_plan_id' : self.meal_plan_id,
            'user_id' : self.user_id,
            'coach_id' : self.coach_id,
            'name' : self.name,
            'description' : self.description,
            'status' : self.status,
            'created_at' : self.created_at,
            'updated_at' : self.updated_at
        }


