from flask import Blueprint
from app.controllers.review_controller import leave_review, get_coach_reviews, delete_review
from app.middleware.auth_middleware import login_required

review_bp = Blueprint('reviews', __name__)

review_bp.route('/coaches/<int:coach_id>/reviews', methods=['GET'])(get_coach_reviews)
review_bp.route('/coaches/<int:coach_id>/reviews', methods=['POST'])(login_required(leave_review))
review_bp.route('/coaches/<int:coach_id>/reviews', methods=['DELETE'])(login_required(delete_review))