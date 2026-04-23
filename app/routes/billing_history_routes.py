from flask import Blueprint
from app.controllers.billing_history_controller import (
    get_my_invoices,
    get_invoice_details,
    get_coach_revenue,
)
from app.middleware.auth_middleware import login_required, coach_required

billing_history_bp = Blueprint('billing_history', __name__)

billing_history_bp.route('/billing/invoices', methods=['GET'])(
    login_required(get_my_invoices)
)
billing_history_bp.route('/billing/invoices/<int:payment_id>', methods=['GET'])(
    login_required(get_invoice_details)
)
billing_history_bp.route('/coach/revenue', methods=['GET'])(
    coach_required(get_coach_revenue)
)
