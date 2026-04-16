from flask import request, jsonify
from app.config.db import db
from app.models.coach import Coach
from app.models.coach_management import CoachManagement
from app.models.user import User
from app.models.notification import Notification
from flask_jwt_extended import get_jwt_identity
from datetime import datetime


def suspend_coach(coach_id):
    """Admin suspends a coach account."""
    coach = Coach.query.filter_by(coach_id=coach_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
    if coach.status == 'suspended':
        return jsonify({'error': 'Coach is already suspended'}), 400

    data = request.get_json() or {}
    admin_id = int(get_jwt_identity())

    coach.status = 'suspended'

    user = User.query.get(coach.user_id)
    if user:
        user.is_active = False

    log = CoachManagement(
        coach_id            = coach_id,
        admin_id            = admin_id,
        action_type         = 'suspend',
        reason              = data.get('reason'),
        suspension_duration = data.get('suspension_duration')
    )
    db.session.add(log)

    notification = Notification(
        user_id = coach.user_id,
        title   = 'Account Suspended',
        message = 'Your coach account has been suspended by an admin. Please contact support.',
        type    = 'system'
    )
    db.session.add(notification)
    db.session.commit()
    return jsonify({'message': 'Coach suspended successfully'}), 200


def reactivate_coach(coach_id):
    """Admin reactivates a suspended coach account."""
    coach = Coach.query.filter_by(coach_id=coach_id, status='suspended').first()
    if not coach:
        return jsonify({'error': 'Coach not found or not suspended'}), 404

    admin_id = int(get_jwt_identity())

    coach.status = 'approved'

    user = User.query.get(coach.user_id)
    if user:
        user.is_active = True

    log = CoachManagement(
        coach_id    = coach_id,
        admin_id    = admin_id,
        action_type = 'reactivate'
    )
    db.session.add(log)

    notification = Notification(
        user_id = coach.user_id,
        title   = 'Account Reactivated',
        message = 'Your coach account has been reactivated. You can now access the platform.',
        type    = 'system'
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

    data = request.get_json() or {}
    admin_id = int(get_jwt_identity())

    coach.status = 'disabled'

    user = User.query.get(coach.user_id)
    if user:
        user.is_active = False

    log = CoachManagement(
        coach_id    = coach_id,
        admin_id    = admin_id,
        action_type = 'disable',
        reason      = data.get('reason')
    )
    db.session.add(log)

    notification = Notification(
        user_id = coach.user_id,
        title   = 'Account Disabled',
        message = 'Your coach account has been permanently disabled. Please contact support.',
        type    = 'system'
    )
    db.session.add(notification)
    db.session.commit()
    return jsonify({'message': 'Coach account disabled successfully'}), 200