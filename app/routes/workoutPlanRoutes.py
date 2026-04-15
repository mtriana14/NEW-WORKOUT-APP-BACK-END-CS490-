from flask import Blueprint
from  app.controllers.WorkoutPlanController import (
    get_client_workout_plans,
    get_all_coach_workout_plans,
    create_workout_plan,
    update_workout_plan,
    delete_workout_plan
)
from app.middleware.auth_middleware import coach_required

workout_plan_bp = Blueprint('workout_plan', __name__)

# Get all workout plans for coach
workout_plan_bp.route('/coach/<int:user_id>/workout-plans', methods=['GET'])(
    get_all_coach_workout_plans
)

# Get workout plans for specific client
workout_plan_bp.route('/coach/<int:user_id>/clients/<int:client_id>/workout-plans', methods=['GET'])(
    get_client_workout_plans
)

# Create new workout plan
workout_plan_bp.route('/coach/<int:user_id>/workout-plans', methods=['POST'])(
    create_workout_plan
)

# Update workout plan
workout_plan_bp.route('/coach/<int:user_id>/workout-plans/<int:plan_id>', methods=['PUT'])(
    update_workout_plan
)

# Delete workout plan
workout_plan_bp.route('/coach/<int:user_id>/workout-plans/<int:plan_id>', methods=['DELETE'])(
    delete_workout_plan
)