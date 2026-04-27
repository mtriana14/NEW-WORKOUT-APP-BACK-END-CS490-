from flask import Blueprint
from app.controllers.mealplan_controller import create_mealplan, delete_mealplan, update_mealplan, get_one_mealplan, get_all_mealplans, add_food_item, get_coach_mealplans, get_client_mealplans
from app.middleware.auth_middleware import coach_required


mealplan_bp = Blueprint('mealplans', __name__)

mealplan_bp.route('/mealplan/create', methods=["POST"])(create_mealplan)
mealplan_bp.route('/mealplan/delete/<int:mealplan_id>', methods=["DELETE"])(delete_mealplan)
mealplan_bp.route('/mealplan/update/<int:mealplan_id>', methods=["PATCH"])(update_mealplan)
mealplan_bp.route('/mealplan/getone/<int:mealplan_id>', methods=["GET"])(get_one_mealplan)
mealplan_bp.route('/mealplan/getall', methods = ["GET"])(get_all_mealplans)
mealplan_bp.route('/mealplan/<int:mealplan_id>/foods', methods=['POST'])(add_food_item)
mealplan_bp.route('/coach/<int:user_id>/meal-plans', methods=['GET'])(coach_required(get_coach_mealplans))
mealplan_bp.route('/coach/<int:user_id>/meal-plans', methods=['POST'], endpoint='coach_create_mealplan')(coach_required(create_mealplan))
mealplan_bp.route('/coach/<int:user_id>/clients/<int:client_id>/meal-plans', methods=['GET'])(coach_required(get_client_mealplans))
mealplan_bp.route('/coach/<int:user_id>/meal-plans/<int:plan_id>', methods=['PUT'], endpoint='coach_update_mealplan')(coach_required(update_mealplan))
mealplan_bp.route('/coach/<int:user_id>/meal-plans/<int:plan_id>', methods=['DELETE'], endpoint='coach_delete_mealplan')(coach_required(delete_mealplan))