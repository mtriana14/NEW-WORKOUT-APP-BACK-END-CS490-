from app.config.db import db
from app.models.client_request import ClientRequest
from app.models.coach import Coach
from app.models.user import User

def seed_client_requests():
    """Seed initial client requests."""

    if ClientRequest.query.count() > 0:
        print('Client requests already seeded, skipping...')
        return

    mike = User.query.filter_by(email='mike.client@fitnessapp.com').first()
    emily = User.query.filter_by(email='emily.client@fitnessapp.com').first()
    john_coach = User.query.filter_by(email='john.coach@fitnessapp.com').first()
    coach = Coach.query.filter_by(user_id=john_coach.id).first()

    requests = [
        ClientRequest(
            client_id=mike.id,
            coach_id=coach.id,
            status='pending',
            message='I want to lose weight and build muscle.'
        ),
        ClientRequest(
            client_id=emily.id,
            coach_id=coach.id,
            status='accepted',
            message='Looking for a personalized fitness plan.'
        ),
    ]

    db.session.add_all(requests)
    db.session.commit()
    print('Client requests seeded successfully')