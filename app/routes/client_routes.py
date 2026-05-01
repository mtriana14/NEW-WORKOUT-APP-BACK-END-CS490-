from flask import Blueprint
from app.controllers.client_controller import (
    get_available_coaches,
    get_coach_details,
    send_coach_request,
    get_my_requests,
    get_my_coach,
    get_my_workout_plans,
    get_my_meal_plans,
    get_pending_request
)
from app.middleware.auth_middleware import login_required
 
client_bp = Blueprint('client', __name__)
 
client_bp.route('/client/coaches', methods=['GET'])(login_required(get_available_coaches))
client_bp.route('/client/coaches/<int:coach_id>', methods=['GET'])(login_required(get_coach_details))
client_bp.route('/client/<int:user_id>/requests', methods=['POST'])(login_required(send_coach_request))
client_bp.route('/client/<int:user_id>/requests', methods=['GET'])(login_required(get_my_requests))
client_bp.route('/client/<int:user_id>/my-coach', methods=['GET'])(login_required(get_my_coach))
client_bp.route('/client/<int:user_id>/workout-plans', methods=['GET'])(login_required(get_my_workout_plans))
client_bp.route('/client/<int:user_id>/meal-plans', methods=['GET'])(login_required(get_my_meal_plans))
client_bp.route('/client/<int:user_id>/pending-request', methods=['GET'])(login_required(get_pending_request))
 