from flask import request, jsonify
from app.config.db import db
from app.models.coach import Coach
from app.models.user import User
from app.models.notification import Notification

def suspend_coach(coach_id):
    """Admin suspends a coach account."""
    coach = Coach.query.filter_by(id=coach_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404

    if coach.status == 'suspended':
        return jsonify({'error': 'Coach is already suspended'}), 400

    # Suspend coach
    coach.status = 'suspended'

    # Disable user account
    user = User.query.filter_by(id=coach.user_id).first()
    user.is_active = False

    # Notify coach
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
    coach = Coach.query.filter_by(id=coach_id, status='suspended').first()
    if not coach:
        return jsonify({'error': 'Coach not found or not suspended'}), 404

    # Reactivate coach
    coach.status = 'approved'

    # Reactivate user account
    user = User.query.filter_by(id=coach.user_id).first()
    user.is_active = True

    # Notify coach
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
    coach = Coach.query.filter_by(id=coach_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404

    if coach.status == 'rejected':
        return jsonify({'error': 'Coach account is already disabled'}), 400

    # Permanently disable
    coach.status = 'rejected'

    # Disable user account
    user = User.query.filter_by(id=coach.user_id).first()
    user.is_active = False

    # Notify coach
    notification = Notification(
        user_id=coach.user_id,
        title='Account Disabled',
        message='Your coach account has been permanently disabled. Please contact support.',
        type='system'
    )

    db.session.add(notification)
    db.session.commit()
    return jsonify({'message': 'Coach account disabled successfully'}), 200