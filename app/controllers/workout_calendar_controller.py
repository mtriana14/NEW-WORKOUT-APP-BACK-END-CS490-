from flask import request, jsonify
from app.config.db import db
from app.models.WorkoutPlan import WorkoutPlan
from app.models.workout_calendar import WorkoutCalendar
from app.models.workout_exercise import WorkoutExercise
from app.models.exercise import Exercise
from flask_jwt_extended import get_jwt_identity, get_jwt
from datetime import datetime, timedelta, date


# UC 3.4 — assign plan to a date

def assign_plan_to_date():
    """
    POST /api/workout-calendar
    Assigns an existing workout plan to a specific date.
    Body: { plan_id, scheduled_date }
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    plan_id = data.get('plan_id')
    scheduled_date = data.get('scheduled_date')

    if not plan_id or not scheduled_date:
        return jsonify({'error': 'plan_id and scheduled_date are required'}), 400

    # Verify plan belongs to this user
    plan = WorkoutPlan.query.filter_by(plan_id=plan_id, user_id=user_id).first()
    if not plan:
        return jsonify({'error': 'Workout plan not found'}), 404

    try:
        parsed_date = datetime.strptime(scheduled_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'scheduled_date must be YYYY-MM-DD'}), 400

    # Check if already scheduled on that date
    existing = WorkoutCalendar.query.filter_by(
        user_id=user_id, plan_id=plan_id, scheduled_date=parsed_date
    ).first()
    if existing:
        return jsonify({'error': 'This plan is already scheduled for that date'}), 409

    entry = WorkoutCalendar(
        user_id=user_id,
        plan_id=plan_id,
        scheduled_date=parsed_date,
        is_completed=False
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({
        'message': 'Plan scheduled successfully',
        'entry': entry.to_dict()
    }), 201


def mark_completed(calendar_id):
    """
    PATCH /api/workout-calendar/<calendar_id>/complete
    Mark a scheduled workout as completed or incomplete.
    Body: { is_completed: true|false }
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    entry = WorkoutCalendar.query.filter_by(
        calendar_id=calendar_id, user_id=user_id
    ).first()
    if not entry:
        return jsonify({'error': 'Calendar entry not found'}), 404

    entry.is_completed = data.get('is_completed', True)
    entry.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': 'Updated successfully',
        'entry': entry.to_dict()
    }), 200


def delete_calendar_entry(calendar_id):
    """
    DELETE /api/workout-calendar/<calendar_id>
    Remove a plan from the calendar.
    """
    user_id = int(get_jwt_identity())

    entry = WorkoutCalendar.query.filter_by(
        calendar_id=calendar_id, user_id=user_id
    ).first()
    if not entry:
        return jsonify({'error': 'Calendar entry not found'}), 404

    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Removed from calendar'}), 200


# UC 3.3 — weekly calendar view 

def get_my_weekly_calendar():
    """
    GET /api/workout-calendar/week?start_date=YYYY-MM-DD
    Returns all scheduled plans for a week window.
    Default is the current week if no start_date provided.
    """
    user_id = int(get_jwt_identity())

    start_str = request.args.get('start_date')
    if start_str:
        try:
            start = datetime.strptime(start_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'start_date must be YYYY-MM-DD'}), 400
    else:
        # Default to Monday of current week
        today = date.today()
        start = today - timedelta(days=today.weekday())

    end = start + timedelta(days=6)

    entries = WorkoutCalendar.query.filter(
        WorkoutCalendar.user_id == user_id,
        WorkoutCalendar.scheduled_date >= start,
        WorkoutCalendar.scheduled_date <= end
    ).order_by(WorkoutCalendar.scheduled_date).all()

    # Group by date
    days = {}
    cursor = start
    while cursor <= end:
        days[cursor.isoformat()] = []
        cursor += timedelta(days=1)

    for entry in entries:
        key = entry.scheduled_date.isoformat()
        if key in days:
            days[key].append(entry.to_dict())

    return jsonify({
        'user_id':    user_id,
        'week_start': start.isoformat(),
        'week_end':   end.isoformat(),
        'calendar':   days
    }), 200


# UC 3.4 — exercises within a plan 

def add_exercise_to_plan(plan_id):
    """
    POST /api/workout-plans/<plan_id>/exercises
    Add an exercise to a workout plan.
    Body: { exercise_id, num_sets, reps, num_length, rest_time, notes, sort_order }
    """
    user_id = int(get_jwt_identity())
    role = get_jwt().get('role')

    plan = WorkoutPlan.query.get(plan_id)
    if not plan:
        return jsonify({'error': 'Workout plan not found'}), 404

    # Client who owns the plan or coach who created it can add exercises
    if role != 'admin' and plan.user_id != user_id:
        from app.models.coach import Coach
        coach = Coach.query.filter_by(user_id=user_id).first()
        if not coach or plan.coach_id != coach.coach_id:
            return jsonify({'error': 'Forbidden'}), 403

    data = request.get_json() or {}
    exercise_id = data.get('exercise_id')
    if not exercise_id:
        return jsonify({'error': 'exercise_id is required'}), 400

    if not Exercise.query.filter_by(e_id=exercise_id, is_active=True).first():
        return jsonify({'error': 'Exercise not found'}), 404

    entry = WorkoutExercise(
        plan_id=plan_id,
        exercise_id=exercise_id,
        num_sets=data.get('num_sets'),
        reps=data.get('reps'),
        num_length=data.get('num_length'),
        rest_time=data.get('rest_time'),
        sort_order=data.get('sort_order', 0),
        notes=data.get('notes'),
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({
        'message': 'Exercise added to plan',
        'entry':   entry.to_dict()
    }), 201


def get_plan_exercises(plan_id):
    """
    GET /api/workout-plans/<plan_id>/exercises
    Returns all exercises in a workout plan.
    """
    plan = WorkoutPlan.query.get(plan_id)
    if not plan:
        return jsonify({'error': 'Workout plan not found'}), 404

    exercises = WorkoutExercise.query.filter_by(plan_id=plan_id)\
        .order_by(WorkoutExercise.sort_order).all()

    return jsonify({
        'plan_id':   plan_id,
        'plan_name': plan.name,
        'exercises': [e.to_dict() for e in exercises]
    }), 200


def remove_exercise_from_plan(plan_id, entry_id):
    """
    DELETE /api/workout-plans/<plan_id>/exercises/<entry_id>
    Remove an exercise from a workout plan.
    """
    user_id = int(get_jwt_identity())
    role = get_jwt().get('role')

    plan = WorkoutPlan.query.get(plan_id)
    if not plan:
        return jsonify({'error': 'Workout plan not found'}), 404

    if role != 'admin' and plan.user_id != user_id:
        from app.models.coach import Coach
        coach = Coach.query.filter_by(user_id=user_id).first()
        if not coach or plan.coach_id != coach.coach_id:
            return jsonify({'error': 'Forbidden'}), 403

    entry = WorkoutExercise.query.filter_by(
        workout_exercises_id=entry_id, plan_id=plan_id
    ).first()
    if not entry:
        return jsonify({'error': 'Exercise entry not found'}), 404

    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Exercise removed from plan'}), 200