from flask import Blueprint
from app.controllers.payment_dashboard_controller import (
    get_payment_summary, get_all_payments, get_coach_payment_summary,
    get_payment_detail, refund_payment
)
from app.middleware.auth_middleware import admin_required

# Blueprint for payment dashboard routes
payment_dashboard_bp = Blueprint('payment_dashboard', __name__)

payment_dashboard_bp.route('/admin/payments/summary', methods=['GET'])(admin_required(get_payment_summary))
payment_dashboard_bp.route('/admin/payments', methods=['GET'])(admin_required(get_all_payments))
payment_dashboard_bp.route('/admin/payments/coach/<int:coach_id>', methods=['GET'])(admin_required(get_coach_payment_summary))
payment_dashboard_bp.route('/admin/payments/stats', methods=['GET'], endpoint='get_payment_stats')(admin_required(get_payment_summary))
payment_dashboard_bp.route('/admin/payments/<int:payment_id>', methods=['GET'])(admin_required(get_payment_detail))
payment_dashboard_bp.route('/admin/payments/<int:payment_id>/refund', methods=['POST'])(admin_required(refund_payment))