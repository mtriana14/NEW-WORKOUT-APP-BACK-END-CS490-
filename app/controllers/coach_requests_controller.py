from flask import request, jsonify
from app.config.db import db
from app.models.client_request import ClientRequest
from app.models.coach import Coach
from app.models.user import User
from app.models.hire import Hire
from app.models.notification import Notification
from datetime import datetime


def get_pending_requests(coach_id):
    """
    GET /api/coach/<coach_id>/requests
    Returns all client requests for a coach (all statuses).
    """
    
    print(coach_id)
    coach = Coach.query.filter_by(coach_id=coach_id).first()
    
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404

    reqs = ClientRequest.query.filter_by(coach_id=2).all()
    result = []

    for req in reqs:
        client_user = User.query.filter_by(user_id=req.client_id).first()
        result.append({
            'request_id':   req.request_id,
            'client_id':    req.client_id,
            'client_name':  f'{client_user.first_name} {client_user.last_name}' if client_user else 'Unknown',
            'client_email': client_user.email if client_user else None,
            'coach_id':     req.coach_id,
            'message':      req.message,
            'status':       req.status,
            'created_at':   str(req.created_at),
            'responded_at': str(req.responded_at) if req.responded_at else None,
        })

    return jsonify({'requests': result}), 200


def respond_to_request(request_id):
    """
    PUT /api/coach/requests/<request_id>/respond
    Body: { action: "accepted" | "declined" }
    """
    data = request.get_json() or {}
    action = data.get('action')

    if action not in ('accepted', 'declined'):
        return jsonify({'error': 'action must be accepted or declined'}), 400

    client_request = ClientRequest.query.filter_by(
        request_id=request_id, status='pending'
    ).first()
    if not client_request:
        return jsonify({'error': 'Request not found or already responded'}), 404

    client_request.status       = action
    client_request.responded_at = datetime.utcnow()

    if action == 'accepted':
        hire = Hire(
            user_id=client_request.client_id,
            coach_id=client_request.coach_id,
            status='active'
        )
        db.session.add(hire)

    notification = Notification(
        user_id=client_request.client_id,
        title='Coaching Request Update',
        message=f'Your coaching request has been {action}.',
        type='request_accepted' if action == 'accepted' else 'request_declined'
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({'message': f'Request {action} successfully'}), 200