from flask import request, jsonify
from app.config.db import db
from app.models.payment import Payment
from app.models.user import User
from app.models.coach import Coach
from app.models.notification import Notification
from sqlalchemy import func


def get_payment_summary():
    """GET /api/admin/payments/summary and /api/admin/payments/stats"""
    total_revenue = db.session.query(
        func.sum(Payment.amount)
    ).filter_by(status='completed').scalar() or 0

    total_transactions = Payment.query.count()

    status_summary = db.session.query(
        Payment.status,
        func.count(Payment.payment_id),
        func.sum(Payment.amount)
    ).group_by(Payment.status).all()

    status_breakdown = [
        {
            'status': row[0],
            'count':  row[1],
            'total':  float(row[2]) if row[2] else 0
        }
        for row in status_summary
    ]

    return jsonify({
        'total_revenue':      float(total_revenue),
        'total_transactions': total_transactions,
        'status_breakdown':   status_breakdown
    }), 200


def get_all_payments():
    """GET /api/admin/payments"""
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)

    payments = Payment.query.order_by(
        Payment.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    # Build user/coach name maps in one query each
    client_ids = {p.client_id for p in payments.items}
    coach_ids  = {p.coach_id  for p in payments.items}

    client_map = {
        u.user_id: f'{u.first_name} {u.last_name}'
        for u in User.query.filter(User.user_id.in_(client_ids)).all()
    }
    coach_user_map = {
        c.coach_id: f'{c.user.first_name} {c.user.last_name}'
        for c in Coach.query.filter(Coach.coach_id.in_(coach_ids)).all()
    }

    result = [
        {
            'id':             p.payment_id,
            'payment_id':     p.payment_id,
            'client_name':    client_map.get(p.client_id, 'Unknown'),
            'coach_name':     coach_user_map.get(p.coach_id, 'Unknown'),
            'amount':         float(p.amount),
            'currency':       p.currency,
            'status':         p.status,
            'payment_method': p.payment_method_type,
            'transaction_id': p.transaction_id,
            'paid_at':        p.paid_at.isoformat() if p.paid_at else None,
            'created_at':     p.created_at.isoformat() if p.created_at else None,
        }
        for p in payments.items
    ]

    return jsonify({
        'payments':     result,
        'total':        payments.total,
        'pages':        payments.pages,
        'current_page': payments.page
    }), 200


def get_payment_detail(payment_id):
    """GET /api/admin/payments/<payment_id>"""
    payment = Payment.query.filter_by(payment_id=payment_id).first()
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404

    client = User.query.filter_by(user_id=payment.client_id).first()
    coach = Coach.query.filter_by(coach_id=payment.coach_id).first()
    coach_user = User.query.filter_by(user_id=coach.user_id).first() if coach else None

    return jsonify({
        'payment': {
            'payment_id': payment.payment_id,
            'client_name': f'{client.first_name} {client.last_name}' if client else 'Unknown',
            'coach_name': f'{coach_user.first_name} {coach_user.last_name}' if coach_user else 'Unknown',
            'amount': float(payment.amount),
            'currency': payment.currency,
            'status': payment.status,
            'payment_method_type': payment.payment_method_type,
            'transaction_id': payment.transaction_id,
            'description': payment.description,
            'paid_at': payment.paid_at.isoformat() if payment.paid_at else None,
            'created_at': payment.created_at.isoformat() if payment.created_at else None,
        }
    }), 200


def refund_payment(payment_id):
    """POST /api/admin/payments/<payment_id>/refund"""
    payment = Payment.query.filter_by(payment_id=payment_id).first()
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404

    if payment.status == 'refunded':
        return jsonify({'error': 'Payment has already been refunded'}), 400

    payment.status = 'refunded'

    notification = Notification(
        user_id=payment.client_id,
        title='Payment Refunded',
        message=f'Your payment of ${float(payment.amount):.2f} has been refunded.',
        type='payment'
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({
        'message': 'Payment refunded successfully',
        'payment_id': payment.payment_id,
        'new_status': payment.status,
    }), 200


def get_coach_payment_summary(coach_id):
    """GET /api/admin/payments/coach/<coach_id>"""
    coach = Coach.query.filter_by(coach_id=coach_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404

    total_earned = db.session.query(
        func.sum(Payment.amount)
    ).filter_by(coach_id=coach_id, status='completed').scalar() or 0

    total_transactions = Payment.query.filter_by(coach_id=coach_id).count()

    return jsonify({
        'coach_id':          coach_id,
        'coach_name':        f'{coach.user.first_name} {coach.user.last_name}',
        'total_earned':      float(total_earned),
        'total_transactions': total_transactions
    }), 200