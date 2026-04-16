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
                'reg_id':   registration.reg_id,
                'user_id':  registration.user_id,
                'applicant': {
                    'name':  f"{user.first_name} {user.last_name}",
                    'email': user.email,
                    'phone': user.phone
                },
                'qualifications':     registration.qualifications,
                'specialty':          registration.specialty,
                'document_links':     registration.document_links,
                'application_status': registration.application_status,
                'created_at':         registration.created_at.isoformat() if registration.created_at else None,
            })

        return jsonify({'Registrations': res}), 200
    except Exception as e:
        print(e)
        return jsonify({"Error": f"{e}"}), 500


def get_all_registrations():
    try:
        regs = db.session.query(
            CoachRegistration, User
        ).join(
            User, CoachRegistration.user_id == User.user_id
        ).order_by(
            CoachRegistration.created_at.desc()
        ).all()

        res = []
        for registration, user in regs:  # return was inside loop — fixed
            res.append({
                'reg_id':   registration.reg_id,
                'user_id':  registration.user_id,
                'applicant': {
                    'name':  f"{user.first_name} {user.last_name}",
                    'email': user.email,
                    'phone': user.phone
                },
                'qualifications':     registration.qualifications,
                'specialty':          registration.specialty,
                'document_links':     registration.document_links,
                'application_status': registration.application_status,
                'created_at':         registration.created_at.isoformat() if registration.created_at else None,
            })

        return jsonify({'Registrations': res}), 200
    except Exception as e:
        print(e)
        return jsonify({"Error": f"{e}"}), 500


def process_coach_registration(reg_id):
    try:
        admin_id = get_jwt_identity()
        data     = request.json or {}
        action   = data.get('action')

        if action not in ['approved', 'rejected']:
            return jsonify({"Error": "Not a valid action. Use 'approved' or 'rejected'"}), 400

        registration = CoachRegistration.query.filter_by(
            reg_id=reg_id, application_status='pending'
        ).first()
        if not registration:
            return jsonify({"Error": "No pending registration found"}), 404

        registration.application_status = action
        registration.reviewed_by        = admin_id

        if action == 'approved':
            # Flip user role
            user = User.query.get(registration.user_id)
            if user:
                user.role = 'coach'

            # Create Coaches row if doesn't exist
            existing_coach = Coach.query.filter_by(user_id=registration.user_id).first()
            if existing_coach:
                existing_coach.status     = 'approved'
                existing_coach.verified_at = datetime.utcnow()
            else:
                new_coach = Coach(
                    user_id        = registration.user_id,
                    specialization = registration.specialty or 'fitness',
                    certifications = registration.qualifications,
                    cost           = data.get('cost', 0.00),
                    status         = 'approved',
                    verified_at    = datetime.utcnow()
                )
                db.session.add(new_coach)

            notif = Notification(
                user_id = registration.user_id,
                title   = 'Coach Application Approved',
                message = f'Your application has been approved on {datetime.utcnow().strftime("%Y-%m-%d")}.',
                type    = 'request_accepted'
            )
            db.session.add(notif)
            db.session.commit()

            return jsonify({
                "Success": "Registration approved",
                "reg_id":  registration.reg_id,
                "user_id": registration.user_id,
            }), 200

        elif action == 'rejected':
            reject_reason = data.get('rejection_reason')
            if not reject_reason:
                return jsonify({"Error": "rejection_reason is required"}), 400

            registration.rejection_reason = reject_reason

            notif = Notification(
                user_id = registration.user_id,
                title   = 'Coach Application Declined',
                message = f'Your application has been denied. Reason: {reject_reason}',
                type    = 'request_declined'
            )
            db.session.add(notif)
            db.session.commit()

            return jsonify({
                "message":          "Registration rejected",
                "reg_id":           registration.reg_id,
                "rejection_reason": registration.rejection_reason,
            }), 200

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"Failed": f"{e}"}), 500