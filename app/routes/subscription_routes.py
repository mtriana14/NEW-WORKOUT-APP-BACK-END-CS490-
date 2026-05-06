from flask import Blueprint
from app.controllers.subscription_controller import subscribe_to_coach , get_my_coach
from app.middleware.auth_middleware import login_required

subscription_bp = Blueprint('subscription', __name__)

subscription_bp.route('/client/subscribe/<int:coach_id>', methods=['POST'])(subscribe_to_coach)
subscription_bp.route('/client/my-coach', methods=['GET'])(get_my_coach)

