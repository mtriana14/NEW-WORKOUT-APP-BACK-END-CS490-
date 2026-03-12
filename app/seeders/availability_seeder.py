from app.config.db import db
from app.models.coach_availability import CoachAvailability
from app.models.coach import Coach
from app.models.user import User
from datetime import time

def seed_availability():
    """Seed initial coach availability."""

    if CoachAvailability.query.count() > 0:
        print('Availability already seeded, skipping...')
        return

    john = User.query.filter_by(email='john.coach@fitnessapp.com').first()
    coach = Coach.query.filter_by(user_id=john.id).first()

    slots = [
        CoachAvailability(
            coach_id=coach.id,
            day_of_week='monday',
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_available=True
        ),
        CoachAvailability(
            coach_id=coach.id,
            day_of_week='wednesday',
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_available=True
        ),
        CoachAvailability(
            coach_id=coach.id,
            day_of_week='friday',
            start_time=time(9, 0),
            end_time=time(13, 0),
            is_available=True
        ),
    ]

    db.session.add_all(slots)
    db.session.commit()
    print('Availability seeded successfully')