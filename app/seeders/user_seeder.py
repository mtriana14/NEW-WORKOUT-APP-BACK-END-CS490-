from app.config.db import db
from app.models.user import User
import bcrypt

def seed_users():
    """Seed initial users - admin, coaches and clients."""

    if User.query.count() > 0:
        print('Users already seeded, skipping...')
        return

    password = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    users = [
        # Admin
        User(
            first_name='Admin',
            last_name='User',
            email='admin@fitnessapp.com',
            password=password,
            role='admin',
            is_active=True
        ),
        # Coaches
        User(
            first_name='John',
            last_name='Smith',
            email='john.coach@fitnessapp.com',
            password=password,
            role='coach',
            is_active=True
        ),
        User(
            first_name='Sarah',
            last_name='Johnson',
            email='sarah.coach@fitnessapp.com',
            password=password,
            role='coach',
            is_active=True
        ),
        # Clients
        User(
            first_name='Mike',
            last_name='Davis',
            email='mike.client@fitnessapp.com',
            password=password,
            role='client',
            is_active=True
        ),
        User(
            first_name='Emily',
            last_name='Brown',
            email='emily.client@fitnessapp.com',
            password=password,
            role='client',
            is_active=True
        ),
    ]

    db.session.add_all(users)
    db.session.commit()
    print('Users seeded successfully')