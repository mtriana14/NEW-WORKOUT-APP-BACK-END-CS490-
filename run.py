from app import create_app
from app.models import User, Coach, CoachAvailability, ClientRequest, Exercise, Notification, Payment, CoachRegistration, CoachManagement

app = create_app()

with app.app_context():
    from app.seeders.run_seeders import run_all_seeders
    run_all_seeders()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
