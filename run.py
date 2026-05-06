import eventlet
eventlet.monkey_patch()
# make sure this stays at the top!!!! ^^^^
from app import create_app, socketio
from app.models import User, Coach, CoachAvailability, ClientRequest, Exercise, Notification, Payment, CoachRegistration, CoachManagement, Hire

app = create_app()

'''
with app.app_context():
    from app.seeders.run_seeders import run_all_seeders
    run_all_seeders()
'''

if __name__ == '__main__':
    socketio.run(app, debug=True)
