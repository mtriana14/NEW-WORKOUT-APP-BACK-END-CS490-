from flask import Blueprint
from app.controllers.billing_controller import (
    get_saved_cards, add_saved_card, delete_saved_card, pay_with_saved_card
)
from app.middleware.auth_middleware import login_required

billing_bp = Blueprint('billing', __name__)

billing_bp.route('/billing/cards', methods=['GET'])(login_required(get_saved_cards))
billing_bp.route('/billing/cards', methods=['POST'])(login_required(add_saved_card))
billing_bp.route('/billing/cards/<int:card_id>', methods=['DELETE'])(login_required(delete_saved_card))
billing_bp.route('/coaches/<int:coach_id>/pay', methods=['POST'])(login_required(pay_with_saved_card))
