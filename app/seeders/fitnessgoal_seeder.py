from app.config.db import db
from app.models.fitnessgoals import FitnessGoal
from datetime import date

def seed_fitnessgoals():
    fitness_goals = [
        FitnessGoal(
            goal_id = 1,
            user_id = 1,
            goal_type = 'Weight Loss',
            target_value = 185.00,
            target_unit = 'lbs',
            deadline = date(2024, 6, 1),
            status = 'active'
        ),
        FitnessGoal(
            goal_id = 2,
            user_id = 1,
            goal_type = 'Strength (Bench Press)',
            target_value = 225.00,
            target_unit = 'lbs',
            deadline = date(2024, 8, 15),
            status = 'active'
        ),
        FitnessGoal(
            goal_id = 3,
            user_id = 1,
            goal_type = 'Running (Marathon)',
            target_value = 26.20,
            target_unit = 'miles',
            deadline = date(2023, 11, 20),
            status = 'completed'
        ),
        FitnessGoal(
            goal_id = 4,
            user_id = 1,
            goal_type = 'Daily Protein Intake',
            target_value = 180.00,
            target_unit = 'grams',
            deadline = date(2024, 12, 31),
            status = 'active'
        ),
        FitnessGoal(
            goal_id = 5,
            user_id = 1,
            goal_type = 'Body Fat Percentage',
            target_value = 12.00,
            target_unit = '%',
            deadline = date(2024, 7, 4),
            status = 'active'
        ),
        FitnessGoal(
            goal_id = 6,
            user_id = 1,
            goal_type = 'Flexibility (Touch Toes)',
            target_value = 1.00,
            target_unit = 'yes/no',
            deadline = date(2023, 1, 1),
            status = 'deleted'
        )
    ]

    db.session.add_all(fitness_goals)
    db.session.commit()
    print("Fitness goals seeded successfully!")