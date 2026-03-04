from app.seeders.user_seeder import seed_users
from app.seeders.coach_seeder import seed_coaches
from app.seeders.availability_seeder import seed_availability
from app.seeders.exercise_seeder import seed_exercises
from app.seeders.client_request_seeder import seed_client_requests

def run_all_seeders():
    """Run all seeders in order."""
    print('Running seeders...')
    seed_users()
    seed_coaches()
    seed_availability()
    seed_exercises()
    seed_client_requests()
    print('All seeders completed successfully')