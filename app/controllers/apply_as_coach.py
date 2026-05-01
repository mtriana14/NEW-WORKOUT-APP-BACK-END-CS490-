from flask import Blueprint
from app.controllers.coach_registration_controller import apply_as_coach, get_my_application
from app.middleware.auth_middleware import login_required

coach_apply_bp = Blueprint('coach_apply', __name__)

coach_apply_bp.route('/coach/apply', methods=['POST'])(login_required(apply_as_coach))
coach_apply_bp.route('/coach/apply', methods=['GET'])(login_required(get_my_application))