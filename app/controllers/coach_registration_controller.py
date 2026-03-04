from flask import request, jsonify
from app.config.db import db
from app.models.coach import Coach
from app.models.user import User
from app.models.notification import Notification
from datetime import datetime

def get_pending_coaches():
    """Get all coaches pending admin review."""
    pending_coaches = Coach.query.filter_by(status='pending').all()
    result = [
        {
            'id': coach.id,
            'user_id': coach.user_id,
            'name': coach.user.name,
            'email': coach.user.email,
            'specialization': coach.specialization,
            'experience_years': coach.experience_years,
            'certifications': coach.certifications,
            'created_at': str(coach.created_at)
        }
        for coach in pending_coaches
    ]
    return jsonify({'pending_coaches': result}), 200


def process_coach_registration(coach_id):
    """Admin approves or rejects a coach registration."""
    data = request.get_json()
    action = data.get('action')

    if action not in ['approved', 'rejected']:
        return jsonify({'error': 'Invalid action, must be approved or rejected'}), 400

    coach = Coach.query.filter_by(id=coach_id, status='pending').first()
    if not coach:
        return jsonify({'error': 'Coach not found or already processed'}), 404

    coach.status = action
    if action == 'approved':
        coach.verified_at = datetime.utcnow()

    notification = Notification(
        user_id=coach.user_id,
        title='Coach Registration Update',
        message=f'Your coach registration has been {action}.',
        type='system'
    )

    db.session.add(notification)
    db.session.commit()
    return jsonify({'message': f'Coach registration {action} successfully'}), 200


def get_all_coaches():
    """Get all coaches with their current status."""
    coaches = Coach.query.all()
    result = [
        {
            'id': coach.id,
            'user_id': coach.user_id,
            'name': coach.user.name,
            'email': coach.user.email,
            'specialization': coach.specialization,
            'status': coach.status,
            'verified_at': str(coach.verified_at) if coach.verified_at else None,
            'created_at': str(coach.created_at)
        }
        for coach in coaches
    ]
    return jsonify({'coaches': result}), 200