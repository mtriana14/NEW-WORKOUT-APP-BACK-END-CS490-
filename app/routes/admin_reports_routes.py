from flask import Blueprint
from app.controllers.admin_reports_controller import (
    get_active_users_report,
    get_role_breakdown_report,
)
from app.middleware.auth_middleware import admin_required

admin_reports_bp = Blueprint('admin_reports', __name__)

admin_reports_bp.route('/admin/reports/active-users', methods=['GET'])(
    admin_required(get_active_users_report)
)
admin_reports_bp.route('/admin/reports/roles', methods=['GET'])(
    admin_required(get_role_breakdown_report)
)
