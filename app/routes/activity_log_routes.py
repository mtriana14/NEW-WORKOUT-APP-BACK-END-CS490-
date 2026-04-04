from flask import Blueprint
from app.controllers.activity_log_controller import (
    log_strength, log_cardio, log_steps_calories, get_my_logs, delete_log
)
from app.middleware.auth_middleware import login_required

activity_log_bp = Blueprint('activity_logs', __name__)

activity_log_bp.route('/logs/strength', methods=['POST'])(login_required(log_strength))
activity_log_bp.route('/logs/cardio', methods=['POST'])(login_required(log_cardio))
activity_log_bp.route('/logs/steps-calories', methods=['POST'])(login_required(log_steps_calories))
activity_log_bp.route('/logs', methods=['GET'])(login_required(get_my_logs))
activity_log_bp.route('/logs/<int:log_id>', methods=['DELETE'])(login_required(delete_log))