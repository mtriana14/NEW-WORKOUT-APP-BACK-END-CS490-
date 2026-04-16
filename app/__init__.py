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
    app.config['DB_PORT'] = os.getenv('DB_PORT', '3306')

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    JWTManager(app)
    init_db(app)

    with app.app_context():
        from app.models import User, Coach, CoachAvailability, ClientRequest, Exercise, Notification, Payment, CoachRegistration, CoachManagement


    from app.routes.client_router import client_bp
    app.register_blueprint(client_bp, url_prefix='/api')

    from app.routes.workoutPlanRoutes import workout_plan_bp
    app.register_blueprint(workout_plan_bp, url_prefix='/api')
    from app.routes.MetalPlanRoutes import meal_plan_bp
    app.register_blueprint(meal_plan_bp, url_prefix='/api')
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
    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix='/api')
    @app.route('/')
    def index():
        return {'message': 'Fitness App API is running'}

    return app
