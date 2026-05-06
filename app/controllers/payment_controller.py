from flask import request, jsonify
from app.config.db import db
from app.models.payment import Payment
from app.models.user import User
from app.models.coach import Coach
from datetime import datetime, date


def _payment_to_dict(p, client_user, coach_user):
    return {
        'payment_id':     p.payment_id,
        'user_id':        p.client_id,
        'client_name':    f'{client_user.first_name} {client_user.last_name}' if client_user else 'Unknown',
        'user_email':     client_user.email if client_user else None,
        'coach_id':       p.coach_id,
        'coach_name':     f'{coach_user.first_name} {coach_user.last_name}' if coach_user else 'Unknown',
        'amount':         float(p.amount) if p.amount else 0,
        'status':         p.status,
        'payment_method': p.payment_method_type,
        'created_at':     p.created_at.isoformat() if p.created_at else None,
    }


def get_all_payments():
    print(request.args)
    """GET /api/admin/payments"""
    status_filter = request.args.get('status')

    query = Payment.query
    if status_filter:
        query = query.filter_by(status=status_filter)

    payments = query.order_by(Payment.created_at.desc()).all()
    result = []

    for p in payments:
        client_user = User.query.filter_by(user_id=p.client_id).first()
        coach       = Coach.query.filter_by(coach_id=p.coach_id).first()
        coach_user  = User.query.filter_by(user_id=coach.user_id).first() if coach else None
        result.append(_payment_to_dict(p, client_user, coach_user))

    # Summary
    all_payments = Payment.query.all()
    now = datetime.utcnow()
    this_month  = [p for p in all_payments if p.created_at and p.created_at.month == now.month and p.created_at.year == now.year]
    last_month_date = date(now.year, now.month - 1 if now.month > 1 else 12, 1)
    last_month  = [p for p in all_payments if p.created_at and p.created_at.month == last_month_date.month and p.created_at.year == last_month_date.year]

    summary = {
        'total_revenue':       sum(float(p.amount) for p in all_payments if p.status == 'completed'),
        'total_transactions':  len(all_payments),
        'completed_payments':  len([p for p in all_payments if p.status == 'completed']),
        'pending_payments':    len([p for p in all_payments if p.status == 'pending']),
        'failed_payments':     len([p for p in all_payments if p.status == 'failed']),
        'this_month_revenue':  sum(float(p.amount) for p in this_month if p.status == 'completed'),
        'last_month_revenue':  sum(float(p.amount) for p in last_month if p.status == 'completed'),
    }

    return jsonify({'payments': result, 'summary': summary}), 200


def get_payment_stats():
    """GET /api/admin/payments/stats"""
    all_payments = Payment.query.all()
    now = datetime.utcnow()

    # Monthly data for last 6 months
    monthly_data = []
    for i in range(5, -1, -1):
        month = now.month - i
        year  = now.year
        while month <= 0:
            month += 12
            year  -= 1
        month_payments = [p for p in all_payments if p.created_at and p.created_at.month == month and p.created_at.year == year]
        monthly_data.append({
            'month':        date(year, month, 1).strftime('%b %Y'),
            'revenue':      sum(float(p.amount) for p in month_payments if p.status == 'completed'),
            'transactions': len(month_payments),
        })

    summary = {
        'total_revenue':      sum(float(p.amount) for p in all_payments if p.status == 'completed'),
        'total_transactions': len(all_payments),
        'completed_payments': len([p for p in all_payments if p.status == 'completed']),
        'pending_payments':   len([p for p in all_payments if p.status == 'pending']),
        'failed_payments':    len([p for p in all_payments if p.status == 'failed']),
        'this_month_revenue': monthly_data[-1]['revenue'] if monthly_data else 0,
        'last_month_revenue': monthly_data[-2]['revenue'] if len(monthly_data) >= 2 else 0,
    }

    return jsonify({'summary': summary, 'monthly_data': monthly_data}), 200