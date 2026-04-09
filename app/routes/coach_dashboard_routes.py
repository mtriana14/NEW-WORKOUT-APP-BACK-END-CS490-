from flask import Blueprint
from app.controllers.coach_dashboard_controller import get_coach_dashboard
from app.middleware.auth_middleware import coach_required

coach_dashboard_bp = Blueprint('coach_dashboard', __name__)

coach_dashboard_bp.route('/coach/dashboard', methods=['GET'])(coach_required(get_coach_dashboard))