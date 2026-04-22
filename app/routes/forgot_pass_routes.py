from flask import Blueprint
from app.controllers.password_reset_controller import forgot_password_reset, reset_password
from app.middleware.auth_middleware import login_required

forgot_pass_bp = Blueprint('forgot_password', __name__)

forgot_pass_bp.route('/password_reset/forgot', methods = ['PATCH'])(forgot_password_reset)
forgot_pass_bp.route('/password_reset', methods = ['PATCH'])(login_required(reset_password))