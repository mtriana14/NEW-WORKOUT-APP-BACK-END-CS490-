from flask import Blueprint
from app.controllers.MetalPlanController import (
    get_client_meal_plans,
    get_all_coach_meal_plans,
    create_meal_plan,
    update_meal_plan,
    delete_meal_plan
)
from app.middleware.auth_middleware import coach_required

meal_plan_bp = Blueprint('meal_plan', __name__)

# Get all meal plans for coach
meal_plan_bp.route('/coach/<int:user_id>/meal-plans', methods=['GET'])(
    get_all_coach_meal_plans
)

# Get meal plans for specific client
meal_plan_bp.route('/coach/<int:user_id>/clients/<int:client_id>/meal-plans', methods=['GET'])(
    get_client_meal_plans
)

# Create new meal plan
meal_plan_bp.route('/coach/<int:user_id>/meal-plans', methods=['POST'])(
    create_meal_plan
)

# Update meal plan
meal_plan_bp.route('/coach/<int:user_id>/meal-plans/<int:plan_id>', methods=['PUT'])(
    update_meal_plan
)

# Delete meal plan
meal_plan_bp.route('/coach/<int:user_id>/meal-plans/<int:plan_id>', methods=['DELETE'])(
   delete_meal_plan
)