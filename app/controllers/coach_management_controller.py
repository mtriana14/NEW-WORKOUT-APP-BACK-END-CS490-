from flask import request, jsonify
from app.config.db import db
from app.models.coach import Coach
from app.models.user import User
from app.models.notification import Notification
 
 
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
 
 
def update_coach_status(coach_id):
    """
    PUT /api/admin/coaches/<coach_id>/status
    Body: { status: 'suspend'|'reactivate'|'disable' }
    Routes to the correct action based on status value.
    """
    data = request.get_json() or {}
    status = data.get('status')
 
    if status == 'suspend':
        return suspend_coach(coach_id)
    elif status == 'reactivate':
        return reactivate_coach(coach_id)
    elif status == 'disable':
        return disable_coach(coach_id)
    else:
        return jsonify({'error': 'Invalid status. Must be suspend, reactivate, or disable'}), 400

def get_all_coaches():
    """GET /api/admin/coaches"""
    coaches = Coach.query.all()
    result = []
    for coach in coaches:
        user = User.query.filter_by(user_id=coach.user_id).first()
        result.append({
            'coach_id':         coach.coach_id,
            'name':             f'{user.first_name} {user.last_name}' if user else 'Unknown',
            'email':            user.email if user else None,
            'specialization':   coach.specialization,
            'experience_years': coach.experience_years,
            'bio':              coach.bio,
            'cost':             float(coach.hourly_rate) if coach.hourly_rate else 0,
            'certifications':   coach.certifications,
            'status':           coach.status,
        })
    return jsonify({'coaches': result}), 200


def get_pending_coaches():
    """GET /api/admin/coaches/pending"""
    coaches = Coach.query.filter_by(status='pending').all()
    result = []
    for coach in coaches:
        user = User.query.filter_by(user_id=coach.user_id).first()
        result.append({
            'coach_id':         coach.coach_id,
            'name':             f'{user.first_name} {user.last_name}' if user else 'Unknown',
            'email':            user.email if user else None,
            'specialization':   coach.specialization,
            'experience_years': coach.experience_years,
            'bio':              coach.bio,
            'cost':             float(coach.hourly_rate) if coach.hourly_rate else 0,
            'certifications':   coach.certifications,
            'status':           coach.status,
        })
    return jsonify({'pending_coaches': result}), 200


def process_coach(coach_id):
    """PUT /api/admin/coaches/<coach_id>/process — approve or reject"""
    data = request.get_json() or {}
    action = data.get('action')

    if action not in ('approved', 'rejected'):
        return jsonify({'error': 'action must be approved or rejected'}), 400

    coach = Coach.query.filter_by(coach_id=coach_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404

    if coach.status != 'pending':
        return jsonify({'error': 'Coach is not pending review'}), 400

    coach.status = action

    user = User.query.filter_by(user_id=coach.user_id).first()
    if user and action == 'rejected':
        user.is_active = False

    notification = Notification(
        user_id=coach.user_id,
        title='Application Update',
        message=f'Your coach application has been {action}.',
        type='system'
    )
    db.session.add(notification)
    db.session.commit()
    return jsonify({'message': f'Coach {action} successfully'}), 200