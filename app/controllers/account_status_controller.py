from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, create_access_token
from app.config.db import db
from app.models.user import User
from datetime import datetime
import bcrypt


def deactivate_my_account():
    """
    PATCH /api/users/me/deactivate
    Marks the caller's account as inactive.
    """
    user_id = int(get_jwt_identity())
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if not user.is_active:
        return jsonify({'message': 'Account is already deactivated'}), 200

    user.is_active = False
    user.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': 'Account deactivated. You can reactivate any time by logging in.',
        'is_active': user.is_active,
    }), 200


def reactivate_account():
    """
    POST /api/users/reactivate
    Public endpoint — accepts email + password and reactivates a deactivated account.
    """
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    try:
        if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({'error': 'Invalid email or password'}), 401
    except (ValueError, AttributeError):
        return jsonify({'error': 'Invalid email or password'}), 401

    if user.is_active:
        token = create_access_token(
            identity=str(user.user_id),
            additional_claims={'role': user.role}
        )
        return jsonify({
            'message': 'Account is already active',
            'token': token,
            'user': {
                'id':         user.user_id,
                'first_name': user.first_name,
                'last_name':  user.last_name,
                'email':      user.email,
                'role':       user.role,
            }
        }), 200

    user.is_active = True
    user.last_login = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    db.session.commit()

    token = create_access_token(
        identity=str(user.user_id),
        additional_claims={'role': user.role}
    )
    return jsonify({
        'message': 'Account reactivated',
        'token': token,
        'user': {
            'id':         user.user_id,
            'first_name': user.first_name,
            'last_name':  user.last_name,
            'email':      user.email,
            'role':       user.role,
        }
    }), 200


def get_account_status():
    """GET /api/users/me/status"""
    user_id = int(get_jwt_identity())
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'user_id':   user.user_id,
        'is_active': user.is_active,
    }), 200
