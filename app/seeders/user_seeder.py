from app.config.db import db
from app.models.user import User
import bcrypt

def seed_users():
    """Seed initial users - admin, coaches and clients."""

    # Check if users already exist
    if User.query.count() > 0:
        print('Users already seeded, skipping...')
        return

    password = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    users = [
        # Admin
        User(
            name='Admin User',
            email='admin@fitnessapp.com',
            password=password,
            role='admin',
            is_active=True
        ),
        # Coaches
        User(
            name='John Smith',
            email='john.coach@fitnessapp.com',
            password=password,
            role='coach',
            is_active=True
        ),
        User(
            name='Sarah Johnson',
            email='sarah.coach@fitnessapp.com',
            password=password,
            role='coach',
            is_active=True
        ),
        # Clients
        User(
            name='Mike Davis',
            email='mike.client@fitnessapp.com',
            password=password,
            role='client',
            is_active=True
        ),
        User(
            name='Emily Brown',
            email='emily.client@fitnessapp.com',
            password=password,
            role='client',
            is_active=True
        ),
    ]

    db.session.add_all(users)
    db.session.commit()
    print('Users seeded successfully')