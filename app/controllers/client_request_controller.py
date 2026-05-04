from flask import request, jsonify
from app.config.db import db
from app.models.client_request import ClientRequest
from app.models.coach import Coach
from app.models.user import User
from app.models.hire import Hire
from app.models.notification import Notification
from flask_jwt_extended import get_jwt_identity
from datetime import datetime


def send_request(coach_id):
    """
    Client sends a coaching request to a coach
    ---
    tags:
      - Coach Hiring
    security:
      - Bearer: []
    parameters:
      - in: path
        name: coach_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Hi, I'm looking for a weight loss program."
    responses:
      201:
        description: Coaching request sent successfully
      400:
        description: Coach not available or missing message
      404:
        description: Coach not found
      409:
        description: Pending request or active hire already exists
    """
    """Client sends a coaching request to a coach."""
    user_id = int(get_jwt_identity())

    # Check coach exists and is active/approved
    coach = Coach.query.filter_by(coach_id=coach_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
    if coach.status not in ['active', 'approved']:
        return jsonify({'error': 'Coach is not available'}), 400

    # Check if client already has a pending request to this coach
    existing = ClientRequest.query.filter_by(
        client_id=user_id,
        coach_id=coach_id,
        status='pending'
    ).first()
    if existing:
        return jsonify({'error': 'You already have a pending request with this coach'}), 409

    # Check if client already has an active hire with this coach
    active_hire = Hire.query.filter_by(
        user_id=user_id,
        coach_id=coach_id,
        status='active'
    ).first()
    if active_hire:
        return jsonify({'error': 'You are already working with this coach'}), 409

    data = request.get_json()

    # Create the request
    try:
        client_request = ClientRequest(
            client_id=user_id,
            coach_id=coach_id,
            message=data.get('message', '') 
        )
        db.session.add(client_request)
    except AttributeError:
        return jsonify({"Error":"No message given"}), 400

    # Notify the coach
    notification = Notification(
        user_id=coach.user_id,
        title='New Coaching Request',
        message='You have received a new coaching request.',
        type='coach_request'
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({
        'message': 'Coaching request sent successfully',
        'request_id': client_request.request_id
    }), 201



def _serialize_dt(value):
    if value is None:
        return None
    return value.isoformat() if hasattr(value, 'isoformat') else str(value)


def _request_dict(req, active_hire_client_ids=None):
    """Serialize a ClientRequest with client name included."""
    client = User.query.filter_by(user_id=req.client_id).first()
    is_active = (
        req.client_id in active_hire_client_ids
        if active_hire_client_ids is not None
        else (req.status == 'accepted')
    )
    return {
        'request_id': req.request_id,
        'client_id': req.client_id,
        'client_name': f'{client.first_name} {client.last_name}' if client else None,
        'client_email': client.email if client else None,
        'coach_id': req.coach_id,
        'message': req.message,
        'status': req.status,
        'is_active': is_active,
        'responded_at': _serialize_dt(req.responded_at),
        'created_at': _serialize_dt(req.created_at),
    }


def get_pending_requests(coach_id):
    """
    Get all pending client requests for a coach
    ---
    tags:
      - Coach Hiring
    security:
      - Bearer: []
    parameters:
      - in: path
        name: coach_id
        type: integer
        required: true
    responses:
      200:
        description: List of pending requests
      404:
        description: Coach not found
    """
    """Get all pending client requests for a coach."""
    coach = Coach.query.filter_by(user_id=coach_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404

    requests = ClientRequest.query.filter_by(coach_id=coach.coach_id, status='pending').all()
    return jsonify({'requests': [_request_dict(req) for req in requests]}), 200


def get_all_requests(coach_id):
    """Get all client requests (any status) for a coach. URL param is user_id."""
    coach = Coach.query.filter_by(user_id=coach_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404

    requests = ClientRequest.query.filter_by(coach_id=coach.coach_id).order_by(
        ClientRequest.created_at.desc()
    ).all()

    # Build set of client_ids that have an active hire with this coach
    active_hires = Hire.query.filter_by(coach_id=coach.coach_id, status='active').all()
    active_hire_client_ids = {h.user_id for h in active_hires}

    return jsonify({'requests': [_request_dict(req, active_hire_client_ids) for req in requests]}), 200


def respond_to_request(request_id):
    """
    Accept or decline a client request
    ---
    tags:
      - Coach Hiring
    security:
      - Bearer: []
    parameters:
      - in: path
        name: request_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - action
          properties:
            action:
              type: string
              enum: [accepted, declined]
    responses:
      200:
        description: Request status updated successfully
      400:
        description: Invalid action provided
      404:
        description: Request not found or already processed
    """
    """Accept or decline a client request."""
    data = request.get_json()
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

     # If accepted, create a Hire record
    if action == 'accepted':
        hire = Hire(
            user_id=client_request.client_id,
            coach_id=client_request.coach_id,
            status='active'
        )
        db.session.add(hire)

    # Notify the client
    notification = Notification(
        user_id=client_request.client_id,
        title='Coaching Request Update',
        message=f'Your coaching request has been {action}.',
        type='request_accepted' if action == 'accepted' else 'request_declined'
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({'message': f'Request {action} successfully'}), 200