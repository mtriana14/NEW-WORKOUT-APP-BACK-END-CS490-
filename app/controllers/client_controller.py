from flask import request, jsonify
from app.config.db import db
from app.models.user import User
from app.models.coach import Coach
from app.models.client_request import ClientRequest
from app.models.WorkoutPlan import WorkoutPlan
from app.models.meal_plan import MealPlan
from app.models.coach_availability import CoachAvailability
 
 
# ==================== COACHES ====================
 
def get_available_coaches():
    """
    GET /api/client/coaches
    Returns all approved coaches for a client to browse.
    """
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
            'name':             f'{user.first_name} {user.last_name}' if user else 'Unknown',
            'email':            user.email if user else None,
            'specialization':   coach.specialization,
            'experience_years': coach.experience_years,
            'bio':              coach.bio,
            'hourly_rate':      float(coach.hourly_rate) if coach.hourly_rate else None,
            'availability':     avail_list
        })
 
    return jsonify({'coaches': result}), 200
 
 
def get_coach_details(coach_id):
    """
    GET /api/client/coaches/<coach_id>
    Returns full profile of a single approved coach.
    """
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
            'name':             f'{user.first_name} {user.last_name}' if user else 'Unknown',
            'email':            user.email if user else None,
            'specialization':   coach.specialization,
            'experience_years': coach.experience_years,
            'bio':              coach.bio,
            'hourly_rate':      float(coach.hourly_rate) if coach.hourly_rate else None,
            'certifications':   coach.certifications,
            'availability':     avail_list
        }
    }), 200
 
 
# ==================== CLIENT REQUESTS ====================
 
def send_coach_request(user_id):
    """
    POST /api/client/<user_id>/requests
    Send a coaching request to a coach.
    Body: { coach_id, message }
    """
    data = request.get_json() or {}
    coach_id = data.get('coach_id')
    message  = data.get('message', '')
 
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
        return jsonify({'error': 'You already have a pending request with this coach'}), 409
 
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
 
 
def get_my_requests(user_id):
    """
    GET /api/client/<user_id>/requests
    Returns all coaching requests sent by this client.
    """
    reqs = ClientRequest.query.filter_by(client_id=user_id).all()
    result = []
 
    for req in reqs:
        coach      = Coach.query.filter_by(coach_id=req.coach_id).first()
        coach_user = User.query.filter_by(user_id=coach.user_id).first() if coach else None
 
        result.append({
            'request_id':   req.request_id,
            'coach_id':     req.coach_id,
            'coach_name':   f'{coach_user.first_name} {coach_user.last_name}' if coach_user else 'Unknown',
            'message':      req.message,
            'status':       req.status,
            'created_at':   str(req.created_at),
            'responded_at': str(req.responded_at) if req.responded_at else None
        })
 
    return jsonify({'requests': result}), 200
 
 
def get_my_coach(user_id):
    """
    GET /api/client/<user_id>/my-coach
    Returns the client's currently active coach or null if none.
    """
    accepted = ClientRequest.query.filter_by(
        client_id=user_id, status='accepted'
    ).first()
 
    if not accepted:
        return jsonify({'coach': None}), 200
 
    coach      = Coach.query.filter_by(coach_id=accepted.coach_id).first()
    coach_user = User.query.filter_by(user_id=coach.user_id).first() if coach else None
 
    return jsonify({
        'coach': {
            'coach_id':       coach.coach_id,
            'name':           f'{coach_user.first_name} {coach_user.last_name}' if coach_user else 'Unknown',
            'email':          coach_user.email if coach_user else None,
            'specialization': coach.specialization,
            'since':          str(accepted.responded_at) if accepted.responded_at else str(accepted.created_at)
        }
    }), 200
 
 
# ==================== WORKOUT PLANS ====================
 
def get_my_workout_plans(user_id):
    """
    GET /api/client/<user_id>/workout-plans
    Returns all workout plans assigned to this client.
    """
    plans  = WorkoutPlan.query.filter_by(user_id=user_id).all()
    result = []
 
    for plan in plans:
        coach      = Coach.query.filter_by(coach_id=plan.coach_id).first()
        coach_user = User.query.filter_by(user_id=coach.user_id).first() if coach else None
 
        result.append({
            'plan_id':     plan.plan_id,
            'name':        plan.name,
            'description': plan.description,
            'status':      plan.status,
            'coach_name':  f'{coach_user.first_name} {coach_user.last_name}' if coach_user else 'Unknown',
            'created_at':  str(plan.created_at),
            'updated_at':  str(plan.updated_at)
        })
 
    return jsonify({'workout_plans': result}), 200
 
 
# ==================== MEAL PLANS ====================
 
def get_my_meal_plans(user_id):
    """
    GET /api/client/<user_id>/meal-plans
    Returns all meal plans assigned to this client.
    """
    plans  = MealPlan.query.filter_by(user_id=user_id).all()
    result = []
 
    for plan in plans:
        coach      = Coach.query.filter_by(coach_id=plan.coach_id).first() if plan.coach_id else None
        coach_user = User.query.filter_by(user_id=coach.user_id).first() if coach else None
 
        result.append({
            'meal_plan_id': plan.meal_plan_id,
            'name':         plan.name,
            'description':  plan.description,
            'status':       plan.status,
            'coach_name':   f'{coach_user.first_name} {coach_user.last_name}' if coach_user else 'Unknown',
            'created_at':   str(plan.created_at),
            'updated_at':   str(plan.updated_at)
        })
 
    return jsonify({'meal_plans': result}), 200