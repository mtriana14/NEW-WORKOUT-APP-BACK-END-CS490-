from app.config.db import db
from app.models.exercise import Exercise
from app.models.user import User

def seed_exercises():
    """Seed initial master exercise database."""

    if Exercise.query.count() > 0:
        print('Exercises already seeded, skipping...')
        return

    admin = User.query.filter_by(email='admin@fitnessapp.com').first()

    exercises = [
        Exercise(
            name='Barbell Squat',
            description='A compound lower body exercise.',
            muscle_group='legs',
            equipment_type='barbell',
            difficulty='intermediate',
            instructions='Stand with feet shoulder width apart, bar on upper back. Squat down until thighs are parallel to floor.',
            created_by=admin.user_id
        ),
        Exercise(
            name='Push Up',
            description='A classic upper body bodyweight exercise.',
            muscle_group='chest',
            equipment_type='bodyweight',
            difficulty='beginner',
            instructions='Start in plank position, lower chest to floor then push back up.',
            created_by=admin.user_id
        ),
        Exercise(
            name='Deadlift',
            description='A compound full body exercise.',
            muscle_group='back',
            equipment_type='barbell',
            difficulty='advanced',
            instructions='Stand with feet hip width apart, hinge at hips to grip bar, drive hips forward to stand.',
            created_by=admin.user_id
        ),
        Exercise(
            name='Pull Up',
            description='An upper body pulling exercise.',
            muscle_group='back',
            equipment_type='bodyweight',
            difficulty='intermediate',
            instructions='Hang from bar with overhand grip, pull chest up to bar.',
            created_by=admin.user_id
        ),
        Exercise(
            name='Plank',
            description='A core stability exercise.',
            muscle_group='core',
            equipment_type='bodyweight',
            difficulty='beginner',
            instructions='Hold push up position with body straight, engage core throughout.',
            created_by=admin.user_id
        ),
    ]

    db.session.add_all(exercises)
    db.session.commit()
    print('Exercises seeded successfully')