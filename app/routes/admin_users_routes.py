from flask import Blueprint
from app.controllers.admin_users_controller import (
    get_all_users,
    update_user_status,
)
from app.middleware.auth_middleware import admin_required

admin_users_bp = Blueprint('admin_users', __name__)

admin_users_bp.route('/admin/users', methods=['GET'])(
    admin_required(get_all_users)
)
admin_users_bp.route('/admin/users/<int:user_id>/status', methods=['PUT'])(
    admin_required(update_user_status)
)