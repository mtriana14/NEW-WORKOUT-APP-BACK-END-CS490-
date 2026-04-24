from flask import Blueprint
from app.controllers.account_status_controller import (
    deactivate_my_account,
    reactivate_account,
    get_account_status,
)
from app.middleware.auth_middleware import login_required

account_status_bp = Blueprint('account_status', __name__)

account_status_bp.route('/users/me/deactivate', methods=['PATCH'])(
    login_required(deactivate_my_account)
)
account_status_bp.route('/users/me/status', methods=['GET'])(
    login_required(get_account_status)
)
# Public — you have to be able to reactivate while logged-out
account_status_bp.route('/users/reactivate', methods=['POST'])(reactivate_account)
