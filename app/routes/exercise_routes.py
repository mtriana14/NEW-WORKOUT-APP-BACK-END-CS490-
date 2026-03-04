from flask import Blueprint
from app.controllers.exercise_controller import (
    get_all_exercises, create_exercise,
    update_exercise, delete_exercise
)
from app.middleware.auth_middleware import admin_required, login_required

# Blueprint for exercise routes
exercise_bp = Blueprint('exercise', __name__)

exercise_bp.route('/admin/exercises', methods=['GET'])(login_required(get_all_exercises))
exercise_bp.route('/admin/exercises', methods=['POST'])(admin_required(create_exercise))
exercise_bp.route('/admin/exercises/<int:exercise_id>', methods=['PUT'])(admin_required(update_exercise))
exercise_bp.route('/admin/exercises/<int:exercise_id>', methods=['DELETE'])(admin_required(delete_exercise))