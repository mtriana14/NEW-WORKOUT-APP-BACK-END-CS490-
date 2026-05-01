from flask import Blueprint
from app.controllers.coach_registration_controller2 import (
    get_pending_registrations, get_all_registrations, process_coach_registration
)
from app.controllers.coach_management_controller import (
    suspend_coach, reactivate_coach, disable_coach, update_coach_status
)
from app.middleware.auth_middleware import admin_required

coach_registration_bp = Blueprint('coach_registration', __name__)

coach_registration_bp.route('/admin/coaches', methods=['GET'])(admin_required(get_all_registrations))
coach_registration_bp.route('/admin/coaches/pending', methods=['GET'])(admin_required(get_pending_registrations))
coach_registration_bp.route('/admin/coaches/<int:reg_id>/process', methods=['PUT'])(admin_required(process_coach_registration))
coach_registration_bp.route('/admin/coaches/<int:coach_id>/suspend', methods=['PUT'])(admin_required(suspend_coach))
coach_registration_bp.route('/admin/coaches/<int:coach_id>/reactivate', methods=['PUT'])(admin_required(reactivate_coach))
coach_registration_bp.route('/admin/coaches/<int:coach_id>/disable', methods=['PUT'])(admin_required(disable_coach))
coach_registration_bp.route('/admin/coaches/<int:coach_id>/status', methods=['PUT'])(admin_required(update_coach_status))