from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.config.db import db
from app.models.coach import Coach
from app.models.coach_availability import CoachAvailability
 
 
def set_availability(user_id=None):
    """
    POST /api/coach/availability
    POST /api/coach/<user_id>/availability
    Set or update coach availability schedule.
    Gets coach from JWT identity.
    """
    jwt_user_id = int(get_jwt_identity())
    coach = Coach.query.filter_by(user_id=jwt_user_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
 
    data = request.get_json() or {}
    slots = data.get('slots', [])
    if not slots:
        return jsonify({'error': 'No availability slots provided'}), 400
 
    # Delete existing and replace with new schedule
    CoachAvailability.query.filter_by(coach_id=coach.coach_id).delete()
 
    for slot in slots:
        availability = CoachAvailability(
            coach_id=coach.coach_id,
            day_of_week=slot.get('day_of_week'),
            start_time=slot.get('start_time'),
            end_time=slot.get('end_time'),
            is_available=slot.get('is_available', True)
        )
        db.session.add(availability)
 
    db.session.commit()
    return jsonify({'message': 'Availability updated successfully'}), 200
 
 
def get_availability(coach_id):
    """
    GET /api/coach/availability/<coach_id>
    Get coach availability by coach_id.
    """
    coach = Coach.query.filter_by(coach_id=coach_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
 
    availability = CoachAvailability.query.filter_by(coach_id=coach_id).all()
    result = [
        {
            'availability_id': slot.availability_id,
            'day_of_week':     slot.day_of_week,
            'start_time':      str(slot.start_time),
            'end_time':        str(slot.end_time),
            'is_available':    slot.is_available
        }
        for slot in availability
    ]
 
    return jsonify({'availability': result}), 200
 
 
def get_availability_by_user(user_id):
    """
    GET /api/coach/<user_id>/availability
    Frontend passes user_id — look up coach_id internally.
    """
    coach = Coach.query.filter_by(user_id=user_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
 
    return get_availability(coach.coach_id)
 