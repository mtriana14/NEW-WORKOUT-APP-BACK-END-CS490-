from flask import request, jsonify
from app.config.db import db
from app.models.progress_entry import ProgressEntry
from datetime import date, timedelta


def _compute_summary(entries):
    """Build summary dict from a list of ProgressEntry objects (ordered date desc)."""
    entries_count = len(entries)
    total_workouts = sum(e.workouts_completed or 0 for e in entries)

    # current streak: consecutive days going back from today with goal_completed=True
    entry_map = {e.entry_date: e for e in entries}
    streak = 0
    check = date.today()
    while check in entry_map and entry_map[check].goal_completed:
        streak += 1
        check -= timedelta(days=1)

    # weekly calories: last 7 days
    week_ago = date.today() - timedelta(days=7)
    weekly_calories = sum(
        e.calories_burned or 0 for e in entries if e.entry_date >= week_ago
    )

    # goals met percentage
    goals_met = sum(1 for e in entries if e.goal_completed)
    goals_met_percentage = round((goals_met / entries_count) * 100, 1) if entries_count else 0

    # weight tracking (entries already ordered desc by date)
    weight_entries = [e for e in entries if e.weight is not None]
    latest_weight = float(weight_entries[0].weight) if weight_entries else None
    weight_change = 0
    if len(weight_entries) >= 2:
        weight_change = round(float(weight_entries[0].weight) - float(weight_entries[-1].weight), 2)

    return {
        'total_workouts': total_workouts,
        'current_streak': streak,
        'weekly_calories': weekly_calories,
        'goals_met_percentage': goals_met_percentage,
        'latest_weight': latest_weight,
        'weight_change': weight_change,
        'entries_count': entries_count,
    }


def get_client_progress(user_id):
    """
    Get progress entries and summary for a client
    ---
    tags:
      - Progress
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
    responses:
      200:
        description: Progress entries with computed summary stats
    """
    entries = (
        ProgressEntry.query
        .filter_by(user_id=user_id)
        .order_by(ProgressEntry.entry_date.desc())
        .all()
    )
    return jsonify({
        'entries': [e.to_dict() for e in entries],
        'summary': _compute_summary(entries),
    }), 200


def save_progress_entry(user_id):
    """
    Save a progress entry for a client
    ---
    tags:
      - Progress
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - entry_date
          properties:
            entry_date:
              type: string
              example: "2026-04-30"
            weight:
              type: number
            workouts_completed:
              type: integer
            calories_burned:
              type: integer
            goal_completed:
              type: boolean
            notes:
              type: string
    responses:
      201:
        description: Progress saved with updated summary
      400:
        description: Missing entry_date
    """
    data = request.get_json() or {}

    if not data.get('entry_date'):
        return jsonify({'error': 'entry_date is required'}), 400

    entry = ProgressEntry(
        user_id=user_id,
        entry_date=data['entry_date'],
        weight=data.get('weight'),
        workouts_completed=data.get('workouts_completed', 0),
        calories_burned=data.get('calories_burned', 0),
        goal_completed=data.get('goal_completed', False),
        notes=data.get('notes'),
    )
    db.session.add(entry)
    db.session.commit()

    all_entries = (
        ProgressEntry.query
        .filter_by(user_id=user_id)
        .order_by(ProgressEntry.entry_date.desc())
        .all()
    )

    return jsonify({
        'message': 'Progress saved',
        'entry': entry.to_dict(),
        'summary': _compute_summary(all_entries),
    }), 201
