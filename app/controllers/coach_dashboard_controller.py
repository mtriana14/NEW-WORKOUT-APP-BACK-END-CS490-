from flask import jsonify
from app.config.db import db
from app.models.coach import Coach
from app.models.hire import Hire
from app.models.payment import Payment
from app.models.activity_log import ActivityLog
from app.models.user import User
from flask_jwt_extended import get_jwt_identity
from datetime import datetime, date
from sqlalchemy import func, extract


def get_coach_dashboard():
    """
    Returns all stats needed for the coach dashboard we have for frontend
    """
    user_id = int(get_jwt_identity())

    # Get the coach record for this user
    coach = Coach.query.filter_by(user_id=user_id).first()
    if not coach:
        return jsonify({'error': 'Coach profile not found'}), 404

    coach_id = coach.coach_id
    today = date.today()
    current_month = today.month
    current_year = today.year

    # Active clients 
    active_hires = Hire.query.filter_by(coach_id=coach_id, status='active').all()
    active_client_count = len(active_hires)
    active_client_ids = [h.user_id for h in active_hires]

    # New hires this month
    new_this_month = Hire.query.filter(
        Hire.coach_id == coach_id,
        Hire.status == 'active',
        extract('month', Hire.created_at) == current_month,
        extract('year', Hire.created_at) == current_year
    ).count()

    # Earnings this month 
    earnings_this_month = db.session.query(func.sum(Payment.amount)).filter(
        Payment.coach_id == coach_id,
        Payment.status == 'completed',
        extract('month', Payment.paid_at) == current_month,
        extract('year', Payment.paid_at) == current_year
    ).scalar() or 0

    # Earnings last month for % change
    last_month = 12 if current_month == 1 else current_month - 1
    last_month_year = current_year - 1 if current_month == 1 else current_year

    earnings_last_month = db.session.query(func.sum(Payment.amount)).filter(
        Payment.coach_id == coach_id,
        Payment.status == 'completed',
        extract('month', Payment.paid_at) == last_month,
        extract('year', Payment.paid_at) == last_month_year
    ).scalar() or 0

    if earnings_last_month > 0:
        earnings_change_pct = round(
            ((float(earnings_this_month) - float(earnings_last_month)) / float(earnings_last_month)) * 100, 1
        )
    else:
        earnings_change_pct = None

    # Monthly revenue for last 6 months for the graph
    monthly_revenue = []
    for i in range(5, -1, -1):
        month = current_month - i
        year = current_year
        if month <= 0:
            month += 12
            year -= 1

        total = db.session.query(func.sum(Payment.amount)).filter(
            Payment.coach_id == coach_id,
            Payment.status == 'completed',
            extract('month', Payment.paid_at) == month,
            extract('year', Payment.paid_at) == year
        ).scalar() or 0

        monthly_revenue.append({
            'month': datetime(year, month, 1).strftime('%b'),
            'year':  year,
            'total': float(total)
        })

    # Recent client activity (last 10 across all active clients) 
    recent_activity = []
    if active_client_ids:
        logs = ActivityLog.query.filter(
            ActivityLog.user_id.in_(active_client_ids),
            ActivityLog.is_deleted == False
        ).order_by(ActivityLog.created_at.desc()).limit(10).all()

        for log in logs:
            client = User.query.get(log.user_id)
            name = f"{client.first_name} {client.last_name[0]}." if client else "Unknown"

            if log.activity_type == 'strength':
                action = f"logged a strength session"
            elif log.activity_type == 'cardio':
                action = f"logged {log.duration_minutes} min of {log.cardio_type}"
            elif log.activity_type == 'steps':
                action = f"logged {log.step_count:,} steps"
            elif log.activity_type == 'calories':
                action = f"logged {log.calorie_intake} calories"
            else:
                action = "logged an activity"

            recent_activity.append({
                'client_name': name,
                'action':      action,
                'log_type':    log.activity_type,
                'log_date':    log.log_date.isoformat() if log.log_date else None,
                'created_at':  log.created_at.isoformat() if log.created_at else None,
            })

    return jsonify({
        'coach_id': coach_id,
        'active_clients': {
            'count':         active_client_count,
            'new_this_month': new_this_month
        },
        'earnings': {
            'this_month':      float(earnings_this_month),
            'last_month':      float(earnings_last_month),
            'change_pct':      earnings_change_pct
        },
        'monthly_revenue':  monthly_revenue,
        'recent_activity':  recent_activity
    }), 200