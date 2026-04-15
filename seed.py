from app import create_app
from app.seeders.seed_all import seed_all

print('Seeding database...')
app = create_app()
with app.app_context():
    seed_all()