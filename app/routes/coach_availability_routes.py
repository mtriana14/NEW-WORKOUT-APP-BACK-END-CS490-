from flask import Blueprint
from app.controllers.coach_availability_controller import set_availability, get_availability, get_availability_by_user
from app.middleware.auth_middleware import coach_required, login_required

# Blueprint for coach availability routes
coach_availability_bp = Blueprint('coach_availability', __name__)

coach_availability_bp.route('/coach/availability', methods=['POST'])(coach_required(set_availability))
coach_availability_bp.route('/coach/availability/<int:coach_id>', methods=['GET'])(login_required(get_availability))
coach_availability_bp.route('/coach/<int:user_id>/availability', methods=['GET'])(login_required(get_availability_by_user))
coach_availability_bp.route('/coach/<int:user_id>/availability', methods=['POST'], endpoint='set_availability_by_user')(coach_required(set_availability))