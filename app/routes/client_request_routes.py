from flask import Blueprint
from app.controllers.client_request_controller import get_pending_requests, respond_to_request , get_all_requests
from app.middleware.auth_middleware import coach_required

# Blueprint for client request routes
client_request_bp = Blueprint('client_request', __name__)

client_request_bp.route('/coach/<int:user_id>/requests', methods=['GET'])(get_pending_requests)
client_request_bp.route('/coach/requests/<int:request_id>/respond', methods=['PUT'])(respond_to_request)
client_request_bp.route('/coach/<int:user_id>/requests/all', methods=['GET'])(get_all_requests)