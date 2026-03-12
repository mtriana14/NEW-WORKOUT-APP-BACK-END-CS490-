from flask import Blueprint
from app.controllers.client_request_controller import get_pending_requests, respond_to_request
from app.middleware.auth_middleware import coach_required

# Blueprint for client request routes
client_request_bp = Blueprint('client_request', __name__)

client_request_bp.route('/coach/<int:coach_id>/requests', methods=['GET'])(coach_required(get_pending_requests))
client_request_bp.route('/coach/requests/<int:request_id>/respond', methods=['PUT'])(coach_required(respond_to_request))