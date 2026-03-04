from flask import Blueprint
from app.controllers.auth_controller import register, login

# Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

auth_bp.route('/auth/register', methods=['POST'])(register)
auth_bp.route('/auth/login', methods=['POST'])(login)