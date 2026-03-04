from flask import request, jsonify
from app.config.db import db
from app.models.client_request import ClientRequest
from app.models.coach import Coach
from app.models.notification import Notification
from datetime import datetime

def get_pending_requests(coach_id):
    """Get all pending client requests for a coach."""
    coach = Coach.query.filter_by(id=coach_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404

    requests = ClientRequest.query.filter_by(coach_id=coach_id, status='pending').all()
    result = [
        {
            'id': req.id,
            'client_id': req.client_id,
            'message': req.message,
            'created_at': str(req.created_at)
        }
        for req in requests
    ]

    return jsonify({'requests': result}), 200


def respond_to_request(request_id):
    """Accept or decline a client request."""
    data = request.get_json()
    action = data.get('action')  # 'accepted' or 'declined'

    if action not in ['accepted', 'declined']:
        return jsonify({'error': 'Invalid action, must be accepted or declined'}), 400

    # Find the request
    client_request = ClientRequest.query.filter_by(id=request_id, status='pending').first()
    if not client_request:
        return jsonify({'error': 'Request not found or already responded'}), 404

    # Update request status
    client_request.status = action
    client_request.responded_at = datetime.utcnow()

    # Send notification to client
    notification = Notification(
        user_id=client_request.client_id,
        title='Coaching Request Update',
        message=f'Your coaching request has been {action}.',
        type='request_accepted' if action == 'accepted' else 'request_declined'
    )

    db.session.add(notification)
    db.session.commit()

    return jsonify({'message': f'Request {action} successfully'}), 200