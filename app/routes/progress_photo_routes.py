from flask import Blueprint
from app.controllers.progress_photo_controller import (
    upload_progress_photo,
    list_my_progress_photos,
    get_client_progress_photos,
    delete_progress_photo,
)
from app.middleware.auth_middleware import login_required, coach_required

progress_photo_bp = Blueprint('progress_photos', __name__)

progress_photo_bp.route('/progress-photos', methods=['POST'])(
    login_required(upload_progress_photo)
)
progress_photo_bp.route('/progress-photos', methods=['GET'])(
    login_required(list_my_progress_photos)
)
progress_photo_bp.route('/progress-photos/<int:photo_id>', methods=['DELETE'])(
    login_required(delete_progress_photo)
)
progress_photo_bp.route('/coach/clients/<int:client_id>/progress-photos', methods=['GET'])(
    coach_required(get_client_progress_photos)
)
