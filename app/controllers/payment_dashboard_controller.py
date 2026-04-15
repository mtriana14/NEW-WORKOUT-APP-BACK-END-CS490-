from flask import request, jsonify
from app.config.db import db
from app.models.payment import Payment
from app.models.user import User
from app.models.coach import Coach
from sqlalchemy import func

def get_payment_summary():
    """Get overall payment summary for admin dashboard."""
    
    # Total revenue from completed payments
    total_revenue = db.session.query(
        func.sum(Payment.amount)
    ).filter_by(status='completed').scalar() or 0

    # Total number of transactions
    total_transactions = Payment.query.count()

    # Transactions by status
    status_summary = db.session.query(
        Payment.status,
        func.count(Payment.id),
        func.sum(Payment.amount)
    ).group_by(Payment.status).all()

    status_breakdown = [
        {
            'status': row[0],
            'count': row[1],
            'total': float(row[2]) if row[2] else 0
        }
        for row in status_summary
    ]

    return jsonify({
        'total_revenue': float(total_revenue),
        'total_transactions': total_transactions,
        'status_breakdown': status_breakdown
    }), 200


def get_all_payments():
    try:
        """Get all payment transactions with details."""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        payments = Payment.query.order_by(Payment.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        result = [
            {
                'id': p.payment_id,
               'client_name': p.client.first_name if p.client else "Unknown",
                 'coach_name': p.coach.user.first_name,
                'amount': float(p.amount),
                'currency': p.currency,
                'status': p.status,
                'payment_method': p.payment_method_type,
                'transaction_id': p.transaction_id,
                'paid_at': str(p.paid_at) if p.paid_at else None,
                'created_at': str(p.created_at)
            }
            for p in payments.items
        ]
        print(result)
        return jsonify({
            'payments': result,
            'total': payments.total,
            'pages': payments.pages,
            'current_page': payments.page
        }), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400


def get_coach_payment_summary(coach_id):
    """Get payment summary for a specific coach."""
    coach = Coach.query.filter_by(id=coach_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404

    total_earned = db.session.query(
        func.sum(Payment.amount)
    ).filter_by(coach_id=coach_id, status='completed').scalar() or 0

    total_transactions = Payment.query.filter_by(coach_id=coach_id).count()

    return jsonify({
        'coach_id': coach_id,
        'coach_name': coach.user.name,
        'total_earned': float(total_earned),
        'total_transactions': total_transactions
    }), 200


def get_payment_stats():
    """Get payment statistics for admin dashboard."""
    payments = Payment.query.all()
    
    total_revenue = sum(float(p.amount) for p in payments if p.status == 'completed')
    total_transactions = len(payments)
    completed = len([p for p in payments if p.status == 'completed'])
    pending = len([p for p in payments if p.status == 'pending'])
    failed = len([p for p in payments if p.status == 'failed'])
    
    return jsonify({
        'total_revenue': total_revenue,
        'total_transactions': total_transactions,
        'completed': completed,
        'pending': pending,
        'failed': failed,
        'success_rate': round((completed / total_transactions * 100), 1) if total_transactions > 0 else 0
    }), 200