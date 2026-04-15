from flask import Blueprint
from app.controllers.coach_registration_controller import (
    get_pending_coaches, process_coach_registration, get_all_coaches , change_coach_status
)
from app.middleware.auth_middleware import admin_required

# Blueprint for coach registration routes
coach_registration_bp = Blueprint('coach_registration', __name__)

coach_registration_bp.route('/admin/coaches', methods=['GET'])( get_all_coaches)
coach_registration_bp.route('/admin/coaches/pending', methods=['GET'])(admin_required(get_pending_coaches))
coach_registration_bp.route('/admin/coaches/<int:coach_id>/process', methods=['PUT'])(admin_required(process_coach_registration))
coach_registration_bp.route('/admin/coaches/<int:coach_id>/status', methods=['PUT'])(change_coach_status)