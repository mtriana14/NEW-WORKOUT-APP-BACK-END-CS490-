from flask import request, jsonify
from app.config.db import db
from app.models.user import User
from app.models.coach import Coach
from app.models.client_request import ClientRequest
from app.models.coach_availability import CoachAvailability
from datetime import datetime


def get_available_coaches():
    """GET /api/client/coaches — browse all approved coaches."""
    coaches = Coach.query.filter_by(status='approved').all()
    result = []

    for coach in coaches:
        user = User.query.filter_by(user_id=coach.user_id).first()
        availability = CoachAvailability.query.filter_by(coach_id=coach.coach_id).all()
        avail_list = [
            {
                'day_of_week': a.day_of_week,
                'start_time':  str(a.start_time),
                'end_time':    str(a.end_time)
            }
            for a in availability if a.is_available
        ]

        result.append({
            'coach_id':         coach.coach_id,
            'user_id':          coach.user_id,
            'name':             f"{user.first_name} {user.last_name}" if user else "Unknown",
            'first_name':       user.first_name if user else None,
            'last_name':        user.last_name if user else None,
            'email':            user.email if user else None,
            'profile_photo':    user.profile_photo if user else None,
            'specialization':   coach.specialization,
            'experience_years': coach.experience_years,
            'certifications':   coach.certifications,
            'bio':              coach.bio,
            'cost':             float(coach.cost) if coach.cost else None,
            'hourly_rate':      float(coach.hourly_rate) if coach.hourly_rate else None,
            'gym':              coach.gym,
            'availability':     avail_list
        })

    return jsonify({'coaches': result}), 200


def get_coach_details(coach_id):
    """GET /api/client/coaches/<coach_id> — view a specific coach's profile."""
    coach = Coach.query.filter_by(coach_id=coach_id, status='approved').first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404

    user = User.query.filter_by(user_id=coach.user_id).first()
    availability = CoachAvailability.query.filter_by(coach_id=coach.coach_id).all()
    avail_list = [
        {
            'day_of_week': a.day_of_week,
            'start_time':  str(a.start_time),
            'end_time':    str(a.end_time)
        }
        for a in availability if a.is_available
    ]

    return jsonify({
        'coach': {
            'coach_id':         coach.coach_id,
            'user_id':          coach.user_id,
            'name':             f"{user.first_name} {user.last_name}" if user else "Unknown",
            'first_name':       user.first_name if user else None,
            'last_name':        user.last_name if user else None,
            'email':            user.email if user else None,
            'profile_photo':    user.profile_photo if user else None,
            'specialization':   coach.specialization,
            'experience_years': coach.experience_years,
            'certifications':   coach.certifications,
            'bio':              coach.bio,
            'cost':             float(coach.cost) if coach.cost else None,
            'hourly_rate':      float(coach.hourly_rate) if coach.hourly_rate else None,
            'gym':              coach.gym,
            'availability':     avail_list
        }
    }), 200


def get_my_coach(user_id):
    """GET /api/client/<user_id>/my-coach — get the client's active coach."""
    from app.models.hire import Hire
    hire = Hire.query.filter_by(user_id=user_id, status='active').first()

    if not hire:
        return jsonify({'coach': None}), 200

    coach = Coach.query.filter_by(coach_id=hire.coach_id).first()
    coach_user = User.query.filter_by(user_id=coach.user_id).first() if coach else None

    return jsonify({
        'coach': {
            'coach_id':       coach.coach_id,
            'name':           f"{coach_user.first_name} {coach_user.last_name}" if coach_user else "Unknown",
            'email':          coach_user.email if coach_user else None,
            'specialization': coach.specialization,
            'since':          hire.created_at.isoformat() if hire.created_at else None
        }
    }), 200


def get_my_requests(user_id):
    """GET /api/client/<user_id>/requests — get all coaching requests for a client."""
    requests = ClientRequest.query.filter_by(client_id=user_id).all()
    result = []

    for req in requests:
        coach = Coach.query.filter_by(coach_id=req.coach_id).first()
        coach_user = User.query.filter_by(user_id=coach.user_id).first() if coach else None

        result.append({
            'request_id':   req.request_id,
            'coach_id':     req.coach_id,
            'coach_name':   f"{coach_user.first_name} {coach_user.last_name}" if coach_user else "Unknown",
            'message':      req.message,
            'status':       req.status,
            'created_at':   str(req.created_at),
            'responded_at': str(req.responded_at) if req.responded_at else None
        })

    return jsonify({'requests': result}), 200


def send_coach_request(user_id):
    """POST /api/client/<user_id>/requests — send a coaching request."""
    data = request.get_json()
    coach_id = data.get('coach_id')
    message = data.get('message', '')

    if not coach_id:
        return jsonify({'error': 'coach_id is required'}), 400

    coach = Coach.query.filter_by(coach_id=coach_id, status='approved').first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404

    existing = ClientRequest.query.filter_by(
        client_id=user_id,
        coach_id=coach_id,
        status='pending'
    ).first()
    if existing:
        return jsonify({'error': 'You already have a pending request with this coach'}), 400

    client_request = ClientRequest(
        client_id=user_id,
        coach_id=coach_id,
        message=message,
        status='pending'
    )
    db.session.add(client_request)
    db.session.commit()

    return jsonify({
        'message':    'Request sent successfully',
        'request_id': client_request.request_id
    }), 201


def get_my_workout_plans(user_id):
    """GET /api/client/<user_id>/workout-plans — get workout plans for a client."""
    from app.models.WorkoutPlan import WorkoutPlan
    plans = WorkoutPlan.query.filter_by(user_id=user_id).all()
    result = []

    for plan in plans:
        coach = Coach.query.filter_by(coach_id=plan.coach_id).first()
        coach_user = User.query.filter_by(user_id=coach.user_id).first() if coach else None

        result.append({
            'plan_id':     plan.plan_id,
            'name':        plan.name,
            'description': plan.description,
            'status':      plan.status,
            'coach_name':  f"{coach_user.first_name} {coach_user.last_name}" if coach_user else "Unknown",
            'created_at':  str(plan.created_at),
            'updated_at':  str(plan.updated_at)
        })

    return jsonify({'workout_plans': result}), 200


def get_my_meal_plans(user_id):
    """GET /api/client/<user_id>/meal-plans — get meal plans for a client."""
    from app.models.meal_plan import MealPlan
    plans = MealPlan.query.filter_by(user_id=user_id).all()
    result = []

    for plan in plans:
        coach = Coach.query.filter_by(coach_id=plan.coach_id).first()
        coach_user = User.query.filter_by(user_id=coach.user_id).first() if coach else None

        result.append({
            'meal_plan_id': plan.meal_plan_id,
            'name':         plan.name,
            'description':  plan.description,
            'status':       plan.status,
            'coach_name':   f"{coach_user.first_name} {coach_user.last_name}" if coach_user else "Unknown",
            'created_at':   str(plan.created_at),
            'updated_at':   str(plan.updated_at)
        })

    return jsonify({'meal_plans': result}), 200