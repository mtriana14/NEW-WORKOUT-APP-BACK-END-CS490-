from app.config.db import db
from app.models.meal_plan import MealPlan

def seed_mealplans():
    meal_plans = [
        MealPlan(
            meal_plan_id = 1,
            user_id = 1,
            coach_id = None,
            name = 'Vegan Diet',
            description = 'A load of plants and plant-based proteins.',
            status = 'active',
        ),
        MealPlan(
            meal_plan_id = 2,
            user_id = 1,
            coach_id = None,
            name = 'Keto Shred',
            description = 'High fat, moderate protein, and ultra-low carb for ketosis.',
            status = 'active',
        ),
        MealPlan(
            meal_plan_id = 3,
            user_id = 1,
            coach_id = None,
            name = 'Bulking Season',
            description = 'High calorie surplus with a focus on complex carbohydrates.',
            status = 'active',
        ),
        MealPlan(
            meal_plan_id = 4,
            user_id = 1,
            coach_id = None,
            name = 'Mediterranean Lifestyle',
            description = 'Heart-healthy fats, lean proteins, and plenty of greens.',
            status = 'active',
        ),
        MealPlan(
            meal_plan_id = 5,
            user_id = 1,
            coach_id = None,
            name = 'Paleo Primal',
            description = 'Focus on whole foods, avoiding processed sugars and grains.',
            status = 'active',
        ),
        MealPlan(
            meal_plan_id = 6,
            user_id = 1,
            coach_id = None,
            name = 'Intermittent Fasting (16:8)',
            description = 'Structured eating window focusing on nutrient density.',
            status = 'active',
        )
    ]
    
    db.session.add_all(meal_plans)
    db.session.commit()
    print("Meal plans seeded successfully!")