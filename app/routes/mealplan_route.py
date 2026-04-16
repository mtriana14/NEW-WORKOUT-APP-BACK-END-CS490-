from flask import Blueprint
from app.controllers.mealplan_controller import create_mealplan, delete_mealplan, update_mealplan, get_one_mealplan, get_all_mealplans

mealplan_bp = Blueprint('mealplans', __name__)

mealplan_bp.route('/mealplan/create', methods=["POST"])(create_mealplan)
mealplan_bp.route('/mealplan/delete/<int:mealplan_id>', methods=["DELETE"])(delete_mealplan)
mealplan_bp.route('/mealplan/update/<int:mealplan_id>', methods=["PATCH"])(update_mealplan)
mealplan_bp.route('/mealplan/getone/<int:mealplan_id>', methods=["GET"])(get_one_mealplan)
mealplan_bp.route('/mealplan/getall', methods = ["GET"])(get_all_mealplans)
mealplan_bp.route('/mealplans/my-plans', methods=['GET'])(get_all_mealplans)