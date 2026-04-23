from flask import Blueprint
from app.controllers.notification_controller import (
    get_all_notifications, get_user_notifications, get_unread_notifications,
    mark_as_read, mark_all_as_read,
    send_notification, delete_notification
)
from app.middleware.auth_middleware import login_required, admin_required

# Blueprint for notification routes
notification_bp = Blueprint('notification', __name__)

notification_bp.route('/notifications/user/<int:user_id>', methods=['GET'])(login_required(get_user_notifications))
notification_bp.route('/notifications/user/<int:user_id>/unread', methods=['GET'])(login_required(get_unread_notifications))
notification_bp.route('/notifications/user/<int:user_id>/read-all', methods=['PUT'])(login_required(mark_all_as_read))
notification_bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])(login_required(mark_as_read))
notification_bp.route('/notifications', methods=['POST'])(admin_required(send_notification))
notification_bp.route('/notifications/<int:notification_id>', methods=['DELETE'])(login_required(delete_notification))
notification_bp.route('/admin/notifications', methods=['GET'])(admin_required(get_all_notifications))