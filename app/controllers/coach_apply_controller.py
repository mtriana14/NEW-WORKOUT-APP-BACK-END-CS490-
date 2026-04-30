from flask import request, jsonify
from app.config.db import db
from app.models.coach_registration import CoachRegistration
from app.models.notification import Notification
from flask_jwt_extended import get_jwt_identity


def apply_as_coach():
    """
    Submit an application to become a coach
    ---
    tags:
      - Coach Onboarding
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            qualifications:
              type: string
              example: "Certified Personal Trainer (NASM)"
            specialty:
              type: string
              example: "Weight Loss & Strength Training"
            document_links:
              type: string
              example: "https://drive.google.com/cert.pdf"
    responses:
      201:
        description: Coach application submitted successfully
      200:
        description: Coach application resubmitted successfully (after previous rejection)
      409:
        description: Already have a pending or approved application
    """
    """
    Logged-in user submits an application to become a coach.
    First-time: creates a CoachRegistrations record (status='pending')
    Previously rejected: updates the record and resets to 'pending'
    Already pending or approved: returns an error
    User role stays as client until admin approves application 
    """
    user_id = int(get_jwt_identity())

    existing = CoachRegistration.query.filter_by(user_id=user_id).first()
    if existing:
        if existing.application_status == 'pending':
            return jsonify({'error': 'You already have a pending coach application'}), 409
        if existing.application_status == 'approved':
            return jsonify({'error': 'Your coach application has already been approved'}), 409
        # Previously rejected — allow reapplication
        data = request.get_json() or {}
        existing.qualifications     = data.get('qualifications', existing.qualifications)
        existing.specialty          = data.get('specialty', existing.specialty)
        existing.document_links     = data.get('document_links', existing.document_links)
        existing.application_status = 'pending'
        existing.rejection_reason   = None
        existing.reviewed_by        = None
        db.session.commit()
        return jsonify({
            'message': 'Coach application resubmitted successfully',
            'reg_id':  existing.reg_id,
            'status':  existing.application_status
        }), 200

    data = request.get_json() or {}

    registration = CoachRegistration(
        user_id        = user_id,
        qualifications = data.get('qualifications'),
        specialty      = data.get('specialty'),
        document_links = data.get('document_links'),
    )
    db.session.add(registration)

    notification = Notification(
        user_id = user_id,
        title   = 'Coach Application Received',
        message = 'Your application to become a coach has been submitted and is under review.',
        type    = 'system'
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({
        'message': 'Coach application submitted successfully',
        'reg_id':  registration.reg_id,
        'status':  registration.application_status
    }), 201


def get_my_application():
    """
    Get the status and details of the current user's coach application
    ---
    tags:
      - Coach Onboarding
    security:
      - Bearer: []
    responses:
      200:
        description: Coach application details
        schema:
          type: object
          properties:
            reg_id:
              type: integer
            application_status:
              type: string
            qualifications:
              type: string
            specialty:
              type: string
            document_links:
              type: string
            rejection_reason:
              type: string
      404:
        description: No coach application found for this user
    """
    """ Returns the logged-in user's coach application status."""
    user_id = int(get_jwt_identity())

    registration = CoachRegistration.query.filter_by(user_id=user_id).first()
    if not registration:
        return jsonify({'error': 'No coach application found'}), 404

    return jsonify({
        'reg_id':             registration.reg_id,
        'application_status': registration.application_status,
        'qualifications':     registration.qualifications,
        'specialty':          registration.specialty,
        'document_links':     registration.document_links,
        'rejection_reason':   registration.rejection_reason,
        'created_at':         registration.created_at.isoformat() if registration.created_at else None,
        'updated_at':         registration.updated_at.isoformat() if registration.updated_at else None,
    }), 200