from app.config.db import db
from datetime import datetime

class MealPlanFood(db.Model):
    __tablename__ = 'mealplanfood'

    item_id      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    meal_plan_id = db.Column(db.Integer, db.ForeignKey('mealplans.meal_plan_id'), nullable=False)
    day_of_week  = db.Column(db.Enum('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'), nullable=False)
    meal_type    = db.Column(db.Enum('breakfast','lunch','dinner','snack'), nullable=False)
    food_name    = db.Column(db.String(255), nullable=False)
    calories     = db.Column(db.Integer, nullable=True)
    protein      = db.Column(db.Numeric(6, 2), nullable=True)
    carbs        = db.Column(db.Numeric(6, 2), nullable=True)
    fat          = db.Column(db.Numeric(6, 2), nullable=True)
    portion_size = db.Column(db.String(100), nullable=True)
    notes        = db.Column(db.Text, nullable=True)
    sort_order   = db.Column(db.Integer, nullable=False, default=0)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    meal_plan = db.relationship('MealPlan', backref='food_items')

    def to_dict(self):
        return {
            'item_id':      self.item_id,
            'meal_plan_id': self.meal_plan_id,
            'day_of_week':  self.day_of_week,
            'meal_type':    self.meal_type,
            'food_name':    self.food_name,
            'calories':     self.calories,
            'protein':      float(self.protein) if self.protein else None,
            'carbs':        float(self.carbs) if self.carbs else None,
            'fat':          float(self.fat) if self.fat else None,
            'portion_size': self.portion_size,
            'notes':        self.notes,
            'sort_order':   self.sort_order,
        }