from flask import request, jsonify
from app.config.db import db
from app.models.client_request import ClientRequest
from app.models.coach import Coach
from app.models.notification import Notification
from datetime import datetime
from app.models.user import User
def get_pending_requests(user_id):
    """Get all pending client requests for a coach."""
    coach = Coach.query.filter_by(user_id=user_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
    
    requests = ClientRequest.query.filter_by(coach_id=coach.coach_id, status='pending').all()
    result = [
        {
            'request_id': req.request_id,
            'client_id': req.client_id,
            'client_name': req.client.first_name if req.client else None,
            'client_email': req.client.email if req.client else None,
            'message': req.message,
            'status': req.status,
            'responded_at': str(req.responded_at) if req.responded_at else None,
            'created_at': str(req.created_at)
        }
        for req in requests
    ]
    return jsonify({'requests': result}), 200


def respond_to_request(request_id):
    """Accept or decline a client request."""
    data = request.get_json()
    print(data)
    print(request_id)
    action = data.get('action')  # 'accepted' or 'declined'

    if action not in ['accepted', 'declined']:
        return jsonify({'error': 'Invalid action, must be accepted or declined'}), 400

    # Find the request
    client_request = ClientRequest.query.filter_by(request_id=request_id, status='pending').first()
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

def get_all_requests(user_id):
    """Get all client requests for a coach (all statuses)."""
     
    coach = Coach.query.filter_by(user_id=user_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
    
    requests = ClientRequest.query.filter_by(coach_id=coach.coach_id).all()
    result = [
        {
            'request_id': req.request_id,
            'client_id': req.client_id,
            'client_name': req.client.first_name if req.client else None,  # User model
            'client_email': req.client.email if req.client else None,      # User model
            'message': req.message,
            'status': req.status,
            'responded_at': str(req.responded_at) if req.responded_at else None,
            'created_at': str(req.created_at)
        }
        for req in requests
    ]
    return jsonify({'requests': result}), 200