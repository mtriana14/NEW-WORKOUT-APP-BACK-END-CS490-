from flask import Blueprint
from app.controllers.coach_management_controller import (
    get_all_coaches, suspend_coach, reactivate_coach, disable_coach,
    update_coach_status, get_coach_detail
)
from app.middleware.auth_middleware import admin_required

# Blueprint for coach management routes
coach_management_bp = Blueprint('coach_management', __name__)

coach_management_bp.route('/admin/coaches', methods=['GET'])(admin_required(get_all_coaches))
coach_management_bp.route('/admin/coaches/<int:coach_id>', methods=['GET'])(admin_required(get_coach_detail))
coach_management_bp.route('/admin/coaches/<int:coach_id>/suspend', methods=['PUT'])(admin_required(suspend_coach))
coach_management_bp.route('/admin/coaches/<int:coach_id>/reactivate', methods=['PUT'])(admin_required(reactivate_coach))
coach_management_bp.route('/admin/coaches/<int:coach_id>/disable', methods=['PUT'])(admin_required(disable_coach))
coach_management_bp.route('/admin/coaches/<int:coach_id>/status', methods=['PUT'])(admin_required(update_coach_status))