from flask import Blueprint
from app.controllers.progress_controller import get_client_progress , save_client_progress
from app.middleware.auth_middleware import login_required

progress_bp = Blueprint('progress', __name__)

progress_bp.route('/client/<int:user_id>/progress', methods=['GET'])(login_required(get_client_progress))
progress_bp.route('/client/<int:user_id>/progress', methods=['POST'])(login_required(save_client_progress))