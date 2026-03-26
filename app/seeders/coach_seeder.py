from app.config.db import db
from app.models.coach import Coach
from app.models.user import User

def seed_coaches():
    """Seed initial coach profiles."""

    if Coach.query.count() > 0:
        print('Coaches already seeded, skipping...')
        return

    john = User.query.filter_by(email='john.coach@fitnessapp.com').first()
    sarah = User.query.filter_by(email='sarah.coach@fitnessapp.com').first()

    coaches = [
        Coach(
            user_id=john.user_id,
            bio='Certified personal trainer with 10 years of experience.',
            specialization='fitness',
            experience_years=10,
            certifications='NASM CPT, ACE',
            hourly_rate=50.00,
            cost=50.00,
            status='approved'
        ),
        Coach(
            user_id=sarah.user_id,
            bio='Nutrition coach specialized in weight loss and muscle gain.',
            specialization='nutrition',
            experience_years=5,
            certifications='Precision Nutrition Level 2',
            hourly_rate=40.00,
            cost=40.00,
            status='pending'
        ),
    ]

    db.session.add_all(coaches)
    db.session.commit()
    print('Coaches seeded successfully')