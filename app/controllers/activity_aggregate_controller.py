from flask import request, jsonify
from app.config.db import db
from app.models.activity_log import ActivityLog
from app.models.hire import Hire
from app.models.coach import Coach
from flask_jwt_extended import get_jwt_identity, get_jwt
from sqlalchemy import func, cast, Date
from datetime import date, datetime, timedelta


# ---------- helpers ---------------------------------------------------------

def _date_range(period):
    """Return (start_date, end_date) for 'week', 'month', or 'year'."""
    today = date.today()
    if period == 'week':
        start = today - timedelta(days=6)      # rolling 7 days inclusive
    elif period == 'month':
        start = today - timedelta(days=29)     # rolling 30 days
    elif period == 'year':
        start = today - timedelta(days=364)    # rolling 365 days
    else:
        start = today - timedelta(days=6)
    return start, today


def _aggregate(user_id, period):
    """
    Build the aggregated payload for one user over a period.
    Returns a dict safe to jsonify.
    """
    start, end = _date_range(period)

    logs = (
        ActivityLog.query
        .filter(ActivityLog.user_id == user_id)
        .filter(ActivityLog.is_deleted == False)  # noqa: E712
        .filter(ActivityLog.log_date >= start)
        .filter(ActivityLog.log_date <= end)
        .all()
    )

    # Per-day buckets keyed by ISO date
    daily = {}
    cursor = start
    while cursor <= end:
        daily[cursor.isoformat()] = {
            'date':             cursor.isoformat(),
            'strength_sessions': 0,
            'cardio_sessions':   0,
            'cardio_minutes':    0,
            'cardio_distance':   0.0,
            'total_sets':        0,
            'total_reps':        0,
            'total_volume':      0.0,    # sets * reps * weight
            'steps':             0,
            'calories':          0,
        }
        cursor += timedelta(days=1)

    # Totals across the whole period
    totals = {
        'strength_sessions': 0,
        'cardio_sessions':   0,
        'cardio_minutes':    0,
        'cardio_distance':   0.0,
        'total_sets':        0,
        'total_reps':        0,
        'total_volume':      0.0,
        'total_steps':       0,
        'total_calories':    0,
        'active_days':       0,
    }

    active_days = set()

    for log in logs:
        key = log.log_date.isoformat()
        if key not in daily:
            continue
        bucket = daily[key]
        active_days.add(key)

        if log.activity_type == 'strength':
            bucket['strength_sessions'] += 1
            totals['strength_sessions'] += 1
            sets = log.sets_completed or 0
            reps = log.reps_completed or 0
            weight = float(log.weight_used) if log.weight_used else 0.0
            bucket['total_sets'] += sets
            bucket['total_reps'] += reps
            bucket['total_volume'] += sets * reps * weight
            totals['total_sets']   += sets
            totals['total_reps']   += reps
            totals['total_volume'] += sets * reps * weight

        elif log.activity_type == 'cardio':
            bucket['cardio_sessions'] += 1
            totals['cardio_sessions'] += 1
            mins = log.duration_minutes or 0
            dist = float(log.distance) if log.distance else 0.0
            bucket['cardio_minutes']  += mins
            bucket['cardio_distance'] += dist
            totals['cardio_minutes']  += mins
            totals['cardio_distance'] += dist

        elif log.activity_type == 'steps':
            steps = log.step_count or 0
            bucket['steps'] += steps
            totals['total_steps'] += steps

        elif log.activity_type == 'calories':
            cals = log.calorie_intake or 0
            bucket['calories'] += cals
            totals['total_calories'] += cals

    totals['active_days'] = len(active_days)

    return {
        'period':     period,
        'start_date': start.isoformat(),
        'end_date':   end.isoformat(),
        'totals':     totals,
        'daily':      list(daily.values()),  # already in date order
    }


# ---------- endpoints -------------------------------------------------------

def get_my_aggregates():
    """
    GET /api/logs/aggregate?period=week|month|year
    Returns aggregated stats for the currently logged-in user.
    """
    user_id = int(get_jwt_identity())
    period = request.args.get('period', 'week').lower()
    if period not in ('week', 'month', 'year'):
        return jsonify({'error': "period must be 'week', 'month', or 'year'"}), 400

    data = _aggregate(user_id, period)
    return jsonify(data), 200


def get_client_aggregates(client_id):
    """
    GET /api/coach/clients/<client_id>/aggregate?period=week|month|year
    Coach-only. Verifies that the coach is actually hired by the client.
    """
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get('role') != 'coach':
        return jsonify({'error': 'Forbidden - coach access required'}), 403

    coach = Coach.query.filter_by(user_id=user_id).first()
    if not coach:
        return jsonify({'error': 'Coach profile not found'}), 404

    # Confirm this coach actually works with this client
    hire = Hire.query.filter_by(
        user_id=client_id, coach_id=coach.coach_id, status='active'
    ).first()
    if not hire:
        return jsonify({'error': 'This client is not assigned to you'}), 403

    period = request.args.get('period', 'week').lower()
    if period not in ('week', 'month', 'year'):
        return jsonify({'error': "period must be 'week', 'month', or 'year'"}), 400

    data = _aggregate(client_id, period)
    data['client_id'] = client_id
    return jsonify(data), 200
