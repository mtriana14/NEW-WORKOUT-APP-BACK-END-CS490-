from flask import Blueprint
from app.controllers.coach_filter_controller import get_subscribed_coach, search_for_coaches
from app.middleware.auth_middleware import login_required

coach_filter_bp = Blueprint('coach_filter', __name__)

coach_filter_bp.route('/getsubbedcoach', methods = ["GET"])(login_required(get_subscribed_coach))
coach_filter_bp.route('/searchcoaches', methods = ["GET"])(search_for_coaches)