from flask import Blueprint
from app.controllers.activity_aggregate_controller import (
    get_my_aggregates,
    get_client_aggregates,
)
from app.middleware.auth_middleware import login_required, coach_required

activity_aggregate_bp = Blueprint('activity_aggregate', __name__)

activity_aggregate_bp.route('/logs/aggregate', methods=['GET'])(
    login_required(get_my_aggregates)
)
activity_aggregate_bp.route('/coach/clients/<int:client_id>/aggregate', methods=['GET'])(
    coach_required(get_client_aggregates)
)
