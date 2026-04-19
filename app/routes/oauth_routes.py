from flask import Blueprint
from app.controllers.oauth_controller import google_sign_in

oauth_bp = Blueprint('oauth', __name__)

oauth_bp.route('/auth/google', methods=['POST'])(google_sign_in)
