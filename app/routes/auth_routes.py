from flask import Blueprint
from app.controllers.auth_controller import register, login, logout
from app.middleware.auth_middleware import login_required

# Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

auth_bp.route('/auth/register', methods=['POST'])(register)
auth_bp.route('/auth/login', methods=['POST'])(login)
auth_bp.route('/auth/logout', methods=['POST'])(login_required(logout))