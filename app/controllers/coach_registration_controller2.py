# app/controllers/coach_registration_controller2.py
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from app.config.db import db
from app.models.coach_registration import CoachRegistration
from app.models.user import User
from app.models.coach import Coach
from app.models.notification import Notification
from datetime import datetime


def get_pending_registrations():
    try:
        pending = db.session.query(
            CoachRegistration, User
        ).join(
            User, CoachRegistration.user_id == User.user_id
        ).filter(
            CoachRegistration.application_status == 'pending'
        ).order_by(
            CoachRegistration.created_at.desc()
        ).all()

        if not pending:
            return jsonify({"Note": "No pending registrations", "registrations": []}), 200

        res = []
        for registration, user in pending:
            res.append({
                'reg_id': registration.reg_id,
                'user_id': registration.user_id,
                'applicant': {
                    'name': f"{user.first_name} {user.last_name}",
                    'email': user.email,
                    'phone': user.phone
                },
                'qualifications': registration.qualifications,
                'specialty': registration.specialty,
                'document_links': registration.document_links,
                'application_status': registration.application_status,
                'created_at': registration.created_at.isoformat() if registration.created_at else None,
                'updated_at': registration.updated_at.isoformat() if registration.updated_at else None
            })

        return jsonify({'Registrations': res}), 200
    except Exception as e:
        print(e)
        return jsonify({"Error": f"{e}"}), 500


def get_all_registrations():
    regs = db.session.query(
        CoachRegistration, User
    ).join(
        User, CoachRegistration.user_id == User.user_id
    ).order_by(
        CoachRegistration.created_at.desc()
    ).all()

    res = []
    for registration, user in regs:
        res.append({
            'reg_id': registration.reg_id,
            'user_id': registration.user_id,
            'applicant': {
                'name': f"{user.first_name} {user.last_name}",
                'email': user.email,
                'phone': user.phone
            },
            'qualifications': registration.qualifications,
            'specialty': registration.specialty,
            'document_links': registration.document_links,
            'application_status': registration.application_status,
            'created_at': registration.created_at.isoformat() if registration.created_at else None,
            'updated_at': registration.updated_at.isoformat() if registration.updated_at else None
        })

    return jsonify({'Registrations': res}), 200  # fixed: outside loop


def process_coach_registration(reg_id):
    try:
        admin_id = get_jwt_identity()
        data = request.json
        action = data.get('action')

        if action not in ["approved", "rejected"]:
            return jsonify({"Error": "Not a valid action"}), 400

        registration = CoachRegistration.query.filter_by(reg_id=reg_id, application_status='pending').first()
        if not registration:
            return jsonify({"Error": "No registration found"}), 404

        if action == "approved":
            registration.application_status = 'approved'
            registration.reviewed_by = admin_id

            existing_check = Coach.query.filter_by(user_id=registration.user_id).first()
            if existing_check:
                return jsonify({"Error": "This coach already exists"}), 400

            new_coach = Coach(
                user_id=registration.user_id,
                certifications=registration.qualifications,
                cost=data.get('cost', 0.00),
                status='active'
            )
            db.session.add(new_coach)

            user = User.query.get(registration.user_id)
            user.role = 'coach'

            notif = Notification(
                user_id=registration.user_id,
                title='Coach Application approved',
                message=f'Your application has been approved at {datetime.utcnow()}',
                type='request_accepted'
            )
            db.session.add(notif)
            db.session.commit()
            return jsonify({
                "Success": "Registration approved",
                "Registration": {
                    'reg_id': registration.reg_id,
                    'user_id': registration.user_id,
                    'application_status': registration.application_status,
                    'reviewed_by': registration.reviewed_by
                }
            }), 200

        elif action == "rejected":  # fixed: was "reject"
            reject_reason = data.get('rejection_reason')
            if not reject_reason:
                return jsonify({"Error": "Reason is required"}), 400

            registration.application_status = 'rejected'
            registration.rejection_reason = reject_reason
            registration.reviewed_by = admin_id

            notif = Notification(
                user_id=registration.user_id,
                title="Coach application declined",
                message=f"Your application has been denied. Reason {reject_reason}",
                type='request_declined'
            )
            db.session.add(notif)
            db.session.commit()

            return jsonify({
                'message': 'Registration rejected',
                'registration': {
                    'reg_id': registration.reg_id,
                    'user_id': registration.user_id,
                    'application_status': registration.application_status,
                    'rejection_reason': registration.rejection_reason,
                    'reviewed_by': registration.reviewed_by
                }
            }), 200

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"Failed": "Could not process registration"}), 500