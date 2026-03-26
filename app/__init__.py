from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from .config.db import init_db
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['DB_HOST'] = os.getenv('DB_HOST')
    app.config['DB_USER'] = os.getenv('DB_USER')
    app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD')
    app.config['DB_NAME'] = os.getenv('DB_NAME')
    app.config['DB_PORT'] = os.getenv('DB_PORT', '3305')

    CORS(app)
    JWTManager(app)
    init_db(app)

    with app.app_context():
        from app.models import User, Coach, CoachAvailability, ClientRequest, Exercise, Notification, Payment, CoachRegistration, CoachManagement, Hire

    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api')
    from app.routes.coach_availability_routes import coach_availability_bp
    app.register_blueprint(coach_availability_bp, url_prefix='/api')
    from app.routes.client_request_routes import client_request_bp
    app.register_blueprint(client_request_bp, url_prefix='/api')
    from app.routes.exercise_routes import exercise_bp
    app.register_blueprint(exercise_bp, url_prefix='/api')
    from app.routes.coach_management_routes import coach_management_bp
    app.register_blueprint(coach_management_bp, url_prefix='/api')
    from app.routes.payment_dashboard_routes import payment_dashboard_bp
    app.register_blueprint(payment_dashboard_bp, url_prefix='/api')
    from app.routes.notification_routes import notification_bp
    app.register_blueprint(notification_bp, url_prefix='/api')
    from app.routes.coach_registration_routes import coach_registration_bp
    app.register_blueprint(coach_registration_bp, url_prefix='/api')
    from app.controllers.getusers import users_bp
    app.register_blueprint(users_bp, url_prefix='/api')
    from app.controllers.update_user import update_user_bp
    app.register_blueprint(update_user_bp, url_prefix='/api')
    from app.controllers.create_user import create_user_bp
    app.register_blueprint(create_user_bp, url_prefix='/api')
    from app.controllers.delete_user import delete_user_bp
    app.register_blueprint(delete_user_bp, url_prefix='/api')
    from app.routes.subscription_routes import subscription_bp
    app.register_blueprint(subscription_bp, url_prefix='/api')
    from app.routes.dismiss_coach_routes import dismiss_coach_bp
    app.register_blueprint(dismiss_coach_bp, url_prefix='/api')
    from app.routes.checkin_routes import checkin_bp
    app.register_blueprint(checkin_bp, url_prefix='/api')
    

    @app.route('/')
    def index():
        return {'message': 'Fitness App API is running'}
    
    @app.route('/testdb')
    def db_check():
        from .config.db import db
        try:
            db.session.execute(db.text('SELECT 1'))
            return {'status': 'ok', 'database': 'connected'}, 200
        except Exception as e:
            return {'status': 'error', 'database': 'unreachable', 'details': str(e)}, 503

    return app
