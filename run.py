from app import create_app
from app.models import User, Coach, CoachAvailability, ClientRequest, Exercise, Notification, Payment, CoachRegistration, CoachManagement
import os
app = create_app()

with app.app_context():
    from app.seeders.run_seeders import run_all_seeders
    #run_all_seeders()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
