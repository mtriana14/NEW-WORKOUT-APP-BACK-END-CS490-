from flask import request, jsonify
from app.config.db import db
from app.models.activity_log import ActivityLog
from flask_jwt_extended import get_jwt_identity
from datetime import datetime


def log_strength():
    """
    Log a strength training session
    ---
    tags:
      - Activity Logs
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - log_date
            - exercise_id
          properties:
            log_date:
              type: string
              example: "2026-04-30"
            exercise_id:
              type: integer
            sets_completed:
              type: integer
            reps_completed:
              type: integer
            weight_used:
              type: number
            notes:
              type: string
    responses:
      201:
        description: Strength session logged successfully
      400:
        description: Missing required fields
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
    Log a cardio activity
    ---
    tags:
      - Activity Logs
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - log_date
            - cardio_type
            - duration_minutes
          properties:
            log_date:
              type: string
              example: "2026-04-30"
            cardio_type:
              type: string
              example: "Running"
            duration_minutes:
              type: integer
            distance:
              type: number
            notes:
              type: string
    responses:
      201:
        description: Cardio activity logged successfully
      400:
        description: Missing required fields
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
    Log daily steps and calorie intake
    ---
    tags:
      - Activity Logs
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - log_date
          properties:
            log_date:
              type: string
              example: "2026-04-30"
            step_count:
              type: integer
            calorie_intake:
              type: integer
            notes:
              type: string
    responses:
      201:
        description: Steps/calories logged successfully
      400:
        description: Missing required fields or no data provided
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    if not data.get('log_date'):
        return jsonify({'error': 'log_date is required'}), 400

    step_count     = data.get('step_count')
    calorie_intake = data.get('calorie_intake')

    if step_count is None and calorie_intake is None:
        return jsonify({'error': 'At least one of step_count or calorie_intake is required'}), 400

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
    Get all personal activity logs
    ---
    tags:
      - Activity Logs
    security:
      - Bearer: []
    parameters:
      - in: query
        name: type
        type: string
        enum: [strength, cardio, steps, calories]
        description: Filter by activity type
      - in: query
        name: date
        type: string
        description: Filter by date (YYYY-MM-DD)
    responses:
      200:
        description: List of activity logs
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
    Soft delete a personal log entry
    ---
    tags:
      - Activity Logs
    security:
      - Bearer: []
    parameters:
      - in: path
        name: log_id
        type: integer
        required: true
        description: ID of the log to delete
    responses:
      200:
        description: Log entry deleted successfully
      404:
        description: Log entry not found
    """
    user_id = int(get_jwt_identity())

    log = ActivityLog.query.filter_by(log_id=log_id, user_id=user_id, is_deleted=False).first()
    if not log:
        return jsonify({'error': 'Log entry not found'}), 404

    log.is_deleted = True
    log.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': f'Log entry {log_id} deleted successfully'}), 200