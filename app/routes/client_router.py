from flask import Blueprint
from app.controllers.client_controller import (
    get_available_coaches,
    get_coach_details,
    get_my_coach,
    get_my_requests,
    send_coach_request,
    get_my_workout_plans,
    get_my_meal_plans
)

client_bp = Blueprint('client', __name__)

# Coach browsing — public
client_bp.route('/client/coaches', methods=['GET'])(get_available_coaches)
client_bp.route('/client/coaches/<int:coach_id>', methods=['GET'])(get_coach_details)

# Client-specific routes
client_bp.route('/client/<int:user_id>/my-coach', methods=['GET'])(get_my_coach)
client_bp.route('/client/<int:user_id>/requests', methods=['GET'])(get_my_requests)
client_bp.route('/client/<int:user_id>/requests', methods=['POST'])(send_coach_request)
client_bp.route('/client/<int:user_id>/workout-plans', methods=['GET'])(get_my_workout_plans)
client_bp.route('/client/<int:user_id>/meal-plans', methods=['GET'])(get_my_meal_plans)