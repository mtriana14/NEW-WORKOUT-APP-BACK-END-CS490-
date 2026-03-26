from flask import Blueprint
from app.controllers.dismiss_coach_controller import dismiss_coach
from app.middleware.auth_middleware import login_required

dismiss_coach_bp = Blueprint('dismiss_coach', __name__)

dismiss_coach_bp.route('/client/dismiss-coach/<int:coach_id>', methods=['PUT'])(login_required(dismiss_coach))