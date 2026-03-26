from flask import jsonify
from app.config.db import db
from app.models.hire import Hire
from app.models.subscription import Subscription
from app.models.notification import Notification
from app.models.coach import Coach
from flask_jwt_extended import get_jwt_identity

def dismiss_coach(coach_id):
    """Dismiss a coach - cancel hire and subscription."""
    user_id = int(get_jwt_identity())

    # Find active hire between client and coach
    hire = Hire.query.filter_by(
        user_id=user_id,
        coach_id=coach_id,
        status='active'
    ).first()

    if not hire:
        return jsonify({'error': 'No active coaching relationship found with this coach'}), 404

    # Cancel the hire
    hire.status = 'cancelled'

    # Cancel active subscription if one exists
    subscription = Subscription.query.filter_by(
        user_id=user_id,
        coach_id=coach_id,
        status='active'
    ).first()

    if subscription:
        subscription.status = 'cancelled'

    # Get coach to find their user_id for notification
    coach = Coach.query.get(coach_id)

    # Notify the coach
    notification = Notification(
        user_id=coach.user_id,
        title='Client Dismissed You',
        message='A client has ended their coaching relationship with you.',
        type='system'
    )

    db.session.add(notification)
    db.session.commit()

    return jsonify({
        'message': 'Coach dismissed successfully'
    }), 200