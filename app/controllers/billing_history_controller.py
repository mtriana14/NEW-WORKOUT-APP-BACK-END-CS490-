from flask import request, jsonify
from app.config.db import db
from app.models.payment import Payment
from app.models.coach import Coach
from app.models.user import User
from app.models.subscription import Subscription
from flask_jwt_extended import get_jwt_identity, get_jwt
from sqlalchemy import func, case
from datetime import datetime, timedelta


def _payment_to_invoice(payment, other_party_name=None):
    return {
        'payment_id':     payment.payment_id,
        'transaction_id': payment.transaction_id,
        'amount':         float(payment.amount),
        'currency':       payment.currency,
        'status':         payment.status,
        'description':    payment.description,
        'paid_at':        payment.paid_at.isoformat() if payment.paid_at else None,
        'created_at':     payment.created_at.isoformat() if payment.created_at else None,
        'method':         payment.payment_method_type,
        'counterparty':   other_party_name,
        'subscription_id': payment.subscription_id,
    }


def get_my_invoices():
    """
    UC 7.3 — GET /api/billing/invoices
    Client-facing: all payments the logged-in user has made.
    Optional query params: ?status=completed&limit=50
    """
    user_id = int(get_jwt_identity())
    status = request.args.get('status')
    try:
        limit = int(request.args.get('limit', 100))
    except ValueError:
        limit = 100

    query = Payment.query.filter_by(client_id=user_id)
    if status:
        query = query.filter_by(status=status)

    payments = query.order_by(
        case((Payment.paid_at.is_(None), 1), else_=0),
        Payment.paid_at.desc()
    ).limit(limit).all()

    # Build a coach_id -> "First Last" lookup in one shot
    coach_ids = {p.coach_id for p in payments}
    coach_map = {}
    if coach_ids:
        rows = (
            db.session.query(Coach.coach_id, User.first_name, User.last_name)
            .join(User, Coach.user_id == User.user_id)
            .filter(Coach.coach_id.in_(coach_ids))
            .all()
        )
        coach_map = {cid: f'{fn} {ln}' for cid, fn, ln in rows}

    total_paid = sum(float(p.amount) for p in payments if p.status == 'completed')

    return jsonify({
        'total_paid': total_paid,
        'count':      len(payments),
        'invoices':   [
            _payment_to_invoice(p, other_party_name=coach_map.get(p.coach_id))
            for p in payments
        ]
    }), 200


def get_invoice_details(payment_id):
    """
    UC 7.3 — GET /api/billing/invoices/<payment_id>
    Returns a single invoice. User can only see their own.
    """
    user_id = int(get_jwt_identity())
    claims = get_jwt()

    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify({'error': 'Invoice not found'}), 404

    # Client can see if it's theirs; admin can see anything
    if payment.client_id != user_id and claims.get('role') != 'admin':
        # Also allow the coach who received it
        coach = Coach.query.filter_by(user_id=user_id).first()
        if not coach or coach.coach_id != payment.coach_id:
            return jsonify({'error': 'Forbidden'}), 403

    coach = Coach.query.get(payment.coach_id)
    coach_user = User.query.get(coach.user_id) if coach else None
    client_user = User.query.get(payment.client_id)

    subscription = None
    if payment.subscription_id:
        sub = Subscription.query.get(payment.subscription_id)
        if sub:
            subscription = {
                'subscription_id': sub.subscription_id,
                'plan_type': sub.plan_type,
                'start_date': str(sub.start_date) if sub.start_date else None,
                'next_billing': str(sub.next_billing) if sub.next_billing else None,
                'status': sub.status,
            }

    return jsonify({
        'invoice': {
            'payment_id':     payment.payment_id,
            'transaction_id': payment.transaction_id,
            'amount':         float(payment.amount),
            'currency':       payment.currency,
            'status':         payment.status,
            'description':    payment.description,
            'paid_at':        payment.paid_at.isoformat() if payment.paid_at else None,
            'created_at':     payment.created_at.isoformat() if payment.created_at else None,
            'method':         payment.payment_method_type,
            'client': {
                'user_id': client_user.user_id if client_user else None,
                'name':    f'{client_user.first_name} {client_user.last_name}' if client_user else None,
                'email':   client_user.email if client_user else None,
            },
            'coach': {
                'coach_id': coach.coach_id if coach else None,
                'name':     f'{coach_user.first_name} {coach_user.last_name}' if coach_user else None,
                'email':    coach_user.email if coach_user else None,
            },
            'subscription': subscription,
        }
    }), 200


def get_coach_revenue():
    """
    UC 7.3 — GET /api/coach/revenue
    Coach-facing: total earnings, earnings this month, and a transactions list.
    Optional params: ?status=completed&limit=100
    """
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get('role') != 'coach':
        return jsonify({'error': 'Forbidden - coach access required'}), 403

    coach = Coach.query.filter_by(user_id=user_id).first()
    if not coach:
        return jsonify({'error': 'Coach profile not found'}), 404

    status = request.args.get('status')
    try:
        limit = int(request.args.get('limit', 100))
    except ValueError:
        limit = 100

    query = Payment.query.filter_by(coach_id=coach.coach_id)
    if status:
        query = query.filter_by(status=status)

    payments = query.order_by(
        case((Payment.paid_at.is_(None), 1), else_=0),
        Payment.paid_at.desc()
    ).limit(limit).all()

    # Aggregate totals (completed only)
    total_earned = (
        db.session.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(Payment.coach_id == coach.coach_id, Payment.status == 'completed')
        .scalar()
    )

    # This month (first of month -> now)
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    month_earned = (
        db.session.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(
            Payment.coach_id == coach.coach_id,
            Payment.status == 'completed',
            Payment.paid_at >= month_start,
        )
        .scalar()
    )

    # Distinct paying clients
    active_clients = (
        db.session.query(func.count(func.distinct(Payment.client_id)))
        .filter(Payment.coach_id == coach.coach_id, Payment.status == 'completed')
        .scalar()
    )

    # Lookup client names for the transactions list
    client_ids = {p.client_id for p in payments}
    client_map = {}
    if client_ids:
        rows = User.query.filter(User.user_id.in_(client_ids)).all()
        client_map = {u.user_id: f'{u.first_name} {u.last_name}' for u in rows}

    return jsonify({
        'summary': {
            'total_earned':   float(total_earned or 0),
            'this_month':     float(month_earned or 0),
            'active_clients': int(active_clients or 0),
            'currency':       'USD',
        },
        'transactions': [
            _payment_to_invoice(p, other_party_name=client_map.get(p.client_id))
            for p in payments
        ],
        'count': len(payments),
    }), 200
