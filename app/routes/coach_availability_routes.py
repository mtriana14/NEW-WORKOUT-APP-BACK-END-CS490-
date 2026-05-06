from flask import Blueprint
from app.controllers.coach_availability_controller import set_availability, get_availability, get_availability_by_user
from app.middleware.auth_middleware import coach_required, login_required
from app.controllers.coach_requests_controller import get_pending_requests, respond_to_request

# Blueprint for coach availability routes
coach_availability_bp = Blueprint('coach_availability', __name__)

coach_availability_bp.route('/coach/availability', methods=['POST'])(coach_required(set_availability))
coach_availability_bp.route('/coach/availability/<int:coach_id>', methods=['GET'])(login_required(get_availability))
coach_availability_bp.route('/coach/<int:user_id>/availability', methods=['GET'])(login_required(get_availability_by_user))
coach_availability_bp.route('/coach/<int:user_id>/availability', methods=['POST'], endpoint='set_availability_by_user')(coach_required(set_availability))


coach_availability_bp.route('/coach/<int:coach_id>/requests', methods=['GET'])(login_required(get_pending_requests))
coach_availability_bp.route('/coach/requests/<int:request_id>/respond', methods=['PUT'])(coach_required(respond_to_request))