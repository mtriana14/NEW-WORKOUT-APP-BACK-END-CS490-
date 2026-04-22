from flask import Blueprint
from app.controllers.workout_calendar_controller import (
    assign_plan_to_date,
    mark_completed,
    delete_calendar_entry,
    get_my_weekly_calendar,
    add_exercise_to_plan,
    get_plan_exercises,
    remove_exercise_from_plan,
)
from app.middleware.auth_middleware import login_required

workout_calendar_bp = Blueprint('workout_calendar', __name__)

# UC 3.3 — weekly calendar view
workout_calendar_bp.route('/workout-calendar/week', methods=['GET'])(login_required(get_my_weekly_calendar))

# UC 3.4 — assign plan to a date
workout_calendar_bp.route('/workout-calendar', methods=['POST'])(login_required(assign_plan_to_date))
workout_calendar_bp.route('/workout-calendar/<int:calendar_id>/complete', methods=['PATCH'])(login_required(mark_completed))
workout_calendar_bp.route('/workout-calendar/<int:calendar_id>', methods=['DELETE'])(login_required(delete_calendar_entry))

# Exercises within a plan
workout_calendar_bp.route('/workout-plans/<int:plan_id>/exercises', methods=['GET'])(login_required(get_plan_exercises))
workout_calendar_bp.route('/workout-plans/<int:plan_id>/exercises', methods=['POST'])(login_required(add_exercise_to_plan))
workout_calendar_bp.route('/workout-plans/<int:plan_id>/exercises/<int:entry_id>', methods=['DELETE'])(login_required(remove_exercise_from_plan))
