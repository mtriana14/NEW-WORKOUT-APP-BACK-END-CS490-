from flask import request, jsonify
from app.config.db import db
from app.models.activity_log import ActivityLog
from flask_jwt_extended import get_jwt_identity
from datetime import datetime


def log_strength():
    """
    UC 4.1 — Log a strength training session.
    Required: log_date, exercise_id, sets_completed, reps_completed
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    if not data.get('log_date'):
        return jsonify({'error': 'log_date is required'}), 400
    if not data.get('exercise_id'):
        return jsonify({'error': 'exercise_id is required'}), 400

    log = ActivityLog(
        user_id        = user_id,
        activity_type  = 'strength',
        exercise_id    = data.get('exercise_id'),
        sets_completed = data.get('sets_completed'),
        reps_completed = data.get('reps_completed'),
        weight_used    = data.get('weight_used'),
        log_date       = data.get('log_date'),
        notes          = data.get('notes'),
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        'message': 'Strength session logged successfully',
        'log': log.to_dict()
    }), 201


def log_cardio():
    """
    UC 4.2 — Log a cardio activity.
    Required: log_date, cardio_type, duration_minutes
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    if not data.get('log_date'):
        return jsonify({'error': 'log_date is required'}), 400
    if not data.get('cardio_type'):
        return jsonify({'error': 'cardio_type is required'}), 400
    if not data.get('duration_minutes'):
        return jsonify({'error': 'duration_minutes is required'}), 400

    log = ActivityLog(
        user_id          = user_id,
        activity_type    = 'cardio',
        cardio_type      = data.get('cardio_type'),
        duration_minutes = data.get('duration_minutes'),
        distance         = data.get('distance'),
        log_date         = data.get('log_date'),
        notes            = data.get('notes'),
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        'message': 'Cardio activity logged successfully',
        'log': log.to_dict()
    }), 201


def log_steps_calories():
    """
    UC 4.3 — Log daily steps and calorie intake.
    Required: log_date, at least one of step_count or calorie_intake
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    if not data.get('log_date'):
        return jsonify({'error': 'log_date is required'}), 400

    step_count     = data.get('step_count')
    calorie_intake = data.get('calorie_intake')

    if step_count is None and calorie_intake is None:
        return jsonify({'error': 'At least one of step_count or calorie_intake is required'}), 400

    # Use 'steps' if step_count provided, otherwise 'calories'
    activity_type = 'steps' if step_count is not None else 'calories'

    log = ActivityLog(
        user_id        = user_id,
        activity_type  = activity_type,
        step_count     = step_count,
        calorie_intake = calorie_intake,
        log_date       = data.get('log_date'),
        notes          = data.get('notes'),
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        'message': 'Steps/calories logged successfully',
        'log': log.to_dict()
    }), 201


def get_my_logs():
    """
    Returns all non-deleted logs for the logged-in user.
    Optional query parameters: ?type=strength|cardio|steps|calories&date=YYYY-MM-DD
    """
    user_id = int(get_jwt_identity())

    query = ActivityLog.query.filter_by(user_id=user_id, is_deleted=False)

    activity_type = request.args.get('type')
    if activity_type:
        query = query.filter_by(activity_type=activity_type)

    log_date = request.args.get('date')
    if log_date:
        query = query.filter_by(log_date=log_date)

    logs = query.order_by(ActivityLog.log_date.desc()).all()

    return jsonify({
        'total': len(logs),
        'logs':  [l.to_dict() for l in logs]
    }), 200


def delete_log(log_id):
    """
    UC 4.4 — Soft delete a personal log entry.
    Only the owner can delete their own log.
    """
    user_id = int(get_jwt_identity())

    log = ActivityLog.query.filter_by(log_id=log_id, user_id=user_id, is_deleted=False).first()
    if not log:
        return jsonify({'error': 'Log entry not found'}), 404

    log.is_deleted = True
    log.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': f'Log entry {log_id} deleted successfully'}), 200