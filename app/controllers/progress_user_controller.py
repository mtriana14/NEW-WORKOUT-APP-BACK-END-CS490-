from flask import request, jsonify
from app.config.db import db
from app.models.progress_entry import ProgressEntry
from datetime import date, timedelta


def _calculate_summary(entries):
    if not entries:
        return {
            'total_workouts':       0,
            'current_streak':       0,
            'weekly_calories':      0,
            'goals_met_percentage': 0,
            'latest_weight':        None,
            'weight_change':        None,
            'entries_count':        0,
        }

    total_workouts = sum(e.workouts_completed for e in entries)

    # Streak
    today = date.today()
    streak = 0
    check = today
    entry_dates = {e.entry_date for e in entries}
    while check in entry_dates:
        streak += 1
        check -= timedelta(days=1)

    # Weekly calories
    week_ago = today - timedelta(days=7)
    weekly_calories = sum(e.calories_burned for e in entries if e.entry_date >= week_ago)

    # Goals met
    goals_met = sum(1 for e in entries if e.goal_completed)
    goals_met_pct = round((goals_met / len(entries)) * 100) if entries else 0

    # Weight
    weights = [e for e in entries if e.weight is not None]
    latest_weight = float(weights[0].weight) if weights else None
    weight_change = None
    if len(weights) >= 2:
        weight_change = round(float(weights[0].weight) - float(weights[-1].weight), 1)

    return {
        'total_workouts':       total_workouts,
        'current_streak':       streak,
        'weekly_calories':      weekly_calories,
        'goals_met_percentage': goals_met_pct,
        'latest_weight':        latest_weight,
        'weight_change':        weight_change,
        'entries_count':        len(entries),
    }


def get_client_progress(user_id):
    """
    GET /api/client/<user_id>/progress
    """
    entries = ProgressEntry.query.filter_by(user_id=user_id).order_by(ProgressEntry.entry_date.desc()).all()
    return jsonify({
        'entries': [e.to_dict() for e in entries],
        'summary': _calculate_summary(entries),
    }), 200


def save_client_progress(user_id):
    """
    POST /api/client/<user_id>/progress
    Creates or updates the entry for a given date.
    """
    data = request.get_json() or {}
    entry_date_str = data.get('entry_date')

    if not entry_date_str:
        return jsonify({'error': 'entry_date is required'}), 400

    entry_date = date.fromisoformat(entry_date_str)

    # Upsert — update if exists, create if not
    entry = ProgressEntry.query.filter_by(user_id=user_id, entry_date=entry_date).first()
    if not entry:
        entry = ProgressEntry(user_id=user_id, entry_date=entry_date)
        db.session.add(entry)

    entry.weight              = data.get('weight')
    entry.workouts_completed  = data.get('workouts_completed', 0)
    entry.calories_burned     = data.get('calories_burned', 0)
    entry.goal_completed      = data.get('goal_completed', False)
    entry.notes               = data.get('notes', '')
    db.session.commit()

    all_entries = ProgressEntry.query.filter_by(user_id=user_id).order_by(ProgressEntry.entry_date.desc()).all()

    return jsonify({
        'message': 'Progress saved successfully',
        'entry':   entry.to_dict(),
        'summary': _calculate_summary(all_entries),
    }), 200