from flask import Blueprint
from app.controllers.subscription_controller import subscribe_to_coach
from app.middleware.auth_middleware import login_required

subscription_bp = Blueprint('subscription', __name__)

subscription_bp.route('/client/subscribe/<int:coach_id>', methods=['POST'])(login_required(subscribe_to_coach))

