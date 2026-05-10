from app.config.db import db
from app.models.coach_availability import CoachAvailability
from app.models.coach import Coach
from app.models.user import User
from datetime import time

def seed_availability():
    """Seed initial coach availability."""

    john = User.query.filter_by(email='john.coach@fitnessapp.com').first()
    if not john:
        print('Coach user not found, skipping availability seeding...')
        return

    coach = Coach.query.filter_by(user_id=john.user_id).first()
    if not coach:
        print('Coach not found, skipping availability seeding...')
        return

    if CoachAvailability.query.filter_by(coach_id=coach.coach_id).first():
        print('Availability already seeded, skipping...')
        return

    slots = [
        CoachAvailability(
            coach_id=coach.coach_id,
            day_of_week='monday',
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_available=True
        ),
        CoachAvailability(
            coach_id=coach.coach_id,
            day_of_week='wednesday',
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_available=True
        ),
        CoachAvailability(
            coach_id=coach.coach_id,
            day_of_week='friday',
            start_time=time(9, 0),
            end_time=time(13, 0),
            is_available=True
        ),
    ]

    db.session.add_all(slots)
    db.session.commit()
    print('Availability seeded successfully')