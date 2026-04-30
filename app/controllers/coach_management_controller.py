from flask import request, jsonify
from app.config.db import db
from app.models.coach import Coach
from app.models.user import User
from app.models.notification import Notification


def _coach_record(coach, user):
    return {
        'id': coach.coach_id,
        'coach_id': coach.coach_id,
        'user_id': coach.user_id,
        'name': f'{user.first_name} {user.last_name}' if user else 'Unknown',
        'email': user.email if user else None,
        'specialization': coach.specialization,
        'certifications': coach.certifications,
        'experience_years': coach.experience_years,
        'bio': coach.bio,
        'hourly_rate': float(coach.hourly_rate) if coach.hourly_rate else None,
        'cost': float(coach.cost) if coach.cost else None,
        'status': coach.status,
        'verified_at': coach.verified_at.isoformat() if coach.verified_at else None,
        'created_at': coach.created_at.isoformat() if coach.created_at else None,
    }


def get_all_coaches():
    """GET /api/admin/coaches - Returns all coaches with user info."""
    coaches = Coach.query.order_by(Coach.created_at.desc()).all()
    user_ids = [c.user_id for c in coaches]
    users = {u.user_id: u for u in User.query.filter(User.user_id.in_(user_ids)).all()}
    result = [_coach_record(coach, users.get(coach.user_id)) for coach in coaches]
    return jsonify({'coaches': result}), 200


def suspend_coach(coach_id):
    """Admin suspends a coach account."""
    coach = Coach.query.filter_by(coach_id=coach_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
 
    if coach.status == 'suspended':
        return jsonify({'error': 'Coach is already suspended'}), 400
 
    coach.status = 'suspended'
 
    user = User.query.filter_by(user_id=coach.user_id).first()
    if user:
        user.is_active = False
 
    notification = Notification(
        user_id=coach.user_id,
        title='Account Suspended',
        message='Your coach account has been suspended by an admin. Please contact support.',
        type='system'
    )
    db.session.add(notification)
    db.session.commit()
    return jsonify({'message': 'Coach suspended successfully'}), 200
 
 
def reactivate_coach(coach_id):
    """Admin reactivates a suspended coach account."""
    coach = Coach.query.filter_by(coach_id=coach_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
 
    if coach.status != 'suspended':
        return jsonify({'error': 'Coach is not suspended'}), 400
 
    coach.status = 'approved'
 
    user = User.query.filter_by(user_id=coach.user_id).first()
    if user:
        user.is_active = True
 
    notification = Notification(
        user_id=coach.user_id,
        title='Account Reactivated',
        message='Your coach account has been reactivated. You can now access the platform.',
        type='system'
    )
    db.session.add(notification)
    db.session.commit()
    return jsonify({'message': 'Coach reactivated successfully'}), 200
 
 
def disable_coach(coach_id):
    """Admin permanently disables a coach account."""
    coach = Coach.query.filter_by(coach_id=coach_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
 
    if coach.status == 'disabled':
        return jsonify({'error': 'Coach account is already disabled'}), 400
 
    coach.status = 'disabled'
 
    user = User.query.filter_by(user_id=coach.user_id).first()
    if user:
        user.is_active = False
 
    notification = Notification(
        user_id=coach.user_id,
        title='Account Disabled',
        message='Your coach account has been permanently disabled. Please contact support.',
        type='system'
    )
    db.session.add(notification)
    db.session.commit()
    return jsonify({'message': 'Coach account disabled successfully'}), 200
 
 
def get_coach_detail(coach_id):
    """GET /api/admin/coaches/<coach_id>"""
    coach = Coach.query.filter_by(coach_id=coach_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404

    user = User.query.filter_by(user_id=coach.user_id).first()

    return jsonify({
        'coach': {
            'coach_id': coach.coach_id,
            'user_id': coach.user_id,
            'name': f'{user.first_name} {user.last_name}' if user else 'Unknown',
            'email': user.email if user else None,
            'specialization': coach.specialization,
            'certifications': coach.certifications,
            'experience_years': coach.experience_years,
            'bio': coach.bio,
            'hourly_rate': float(coach.hourly_rate) if coach.hourly_rate else None,
            'cost': float(coach.cost) if coach.cost else None,
            'status': coach.status,
            'verified_at': coach.verified_at.isoformat() if coach.verified_at else None,
            'created_at': coach.created_at.isoformat() if coach.created_at else None,
        }
    }), 200


def approve_coach(coach_id):
    """Set a coach's status to approved."""
    coach = Coach.query.filter_by(coach_id=coach_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
    coach.status = 'approved'
    notification = Notification(
        user_id=coach.user_id,
        title='Coach Account Approved',
        message='Your coach account has been approved. You can now accept clients.',
        type='system'
    )
    db.session.add(notification)
    db.session.commit()
    return jsonify({'message': 'Coach approved successfully'}), 200


def reject_coach(coach_id):
    """Set a coach's status to rejected."""
    coach = Coach.query.filter_by(coach_id=coach_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
    coach.status = 'rejected'
    notification = Notification(
        user_id=coach.user_id,
        title='Coach Account Rejected',
        message='Your coach account application has been rejected. Please contact support.',
        type='system'
    )
    db.session.add(notification)
    db.session.commit()
    return jsonify({'message': 'Coach rejected successfully'}), 200


def update_coach_status(coach_id):
    """
    PUT /api/admin/coaches/<coach_id>/status
    Body: { status: 'suspend'|'reactivate'|'disable'|'approved'|'rejected' }
    Also accepts { action: 'approved'|'rejected' } for compatibility.
    """
    data = request.get_json() or {}
    status = data.get('status') or data.get('action')

    if status == 'suspend':
        return suspend_coach(coach_id)
    elif status == 'reactivate':
        return reactivate_coach(coach_id)
    elif status == 'disable':
        return disable_coach(coach_id)
    elif status in ('approved', 'approve'):
        return approve_coach(coach_id)
    elif status in ('rejected', 'reject'):
        return reject_coach(coach_id)
    else:
        return jsonify({'error': 'Invalid status. Must be suspend, reactivate, disable, approved, or rejected'}), 400