from flask import request, jsonify
from app.config.db import db
from app.models.coach import Coach
from app.models.coach_availability import CoachAvailability

def set_availability():
    """Set or update coach availability schedule."""
    data = request.get_json()
    coach_id = data.get('coach_id')

    # Validate coach exists and is approved
    coach = Coach.query.filter_by(id=coach_id, status='approved').first()
    if not coach:
        return jsonify({'error': 'Coach not found or not approved'}), 404

    # Delete existing availability and replace with new schedule
    CoachAvailability.query.filter_by(coach_id=coach_id).delete()

    slots = data.get('slots', [])
    if not slots:
        return jsonify({'error': 'No availability slots provided'}), 400

    for slot in slots:
        availability = CoachAvailability(
            coach_id=coach_id,
            day_of_week=slot.get('day_of_week'),
            start_time=slot.get('start_time'),
            end_time=slot.get('end_time'),
            is_available=slot.get('is_available', True)
        )
        db.session.add(availability)

    db.session.commit()
    return jsonify({'message': 'Availability updated successfully'}), 200


def get_availability(coach_id):
    """Get coach availability schedule."""
    coach = Coach.query.filter_by(id=coach_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404

    availability = CoachAvailability.query.filter_by(coach_id=coach_id).all()
    result = [
        {
            'id': slot.id,
            'day_of_week': slot.day_of_week,
            'start_time': str(slot.start_time),
            'end_time': str(slot.end_time),
            'is_available': slot.is_available
        }
        for slot in availability
    ]

    return jsonify({'availability': result}), 200