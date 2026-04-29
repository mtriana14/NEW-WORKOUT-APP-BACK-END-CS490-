from flask import Blueprint
from app.controllers.exercise_controller import (
    get_all_exercises, get_exercise_by_id, create_exercise,
    update_exercise, delete_exercise, bulk_create_common_exercises
)
from app.middleware.auth_middleware import admin_required, login_required

exercise_bp = Blueprint('exercise', __name__)

# /common must be registered before /<int:exercise_id> to avoid Flask
# trying to match the string 'common' as an integer
exercise_bp.route('/admin/exercises/common', methods=['POST'])(admin_required(bulk_create_common_exercises))

exercise_bp.route('/admin/exercises', methods=['GET'])(login_required(get_all_exercises))
exercise_bp.route('/admin/exercises', methods=['POST'])(admin_required(create_exercise))
exercise_bp.route('/admin/exercises/<int:exercise_id>', methods=['GET'])(login_required(get_exercise_by_id))
exercise_bp.route('/admin/exercises/<int:exercise_id>', methods=['PUT'])(admin_required(update_exercise))
exercise_bp.route('/admin/exercises/<int:exercise_id>', methods=['DELETE'])(admin_required(delete_exercise))
