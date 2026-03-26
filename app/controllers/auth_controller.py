from flask import request, jsonify
from app.config.db import db
from app.models.user import User
from flask_jwt_extended import create_access_token, get_jwt_identity
import bcrypt

def register():
    """Register a new user account."""
    data = request.get_json()

    # Validate required fields
    if not data.get('first_name') or not data.get('last_name') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'First name, last name, email and password are required'}), 400

    # Check if email already exists
    existing = User.query.filter_by(email=data.get('email')).first()
    if existing:
        return jsonify({'error': 'An account with this email already exists'}), 409

    # Hash password
    hashed = bcrypt.hashpw(data.get('password').encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = User(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        username=data.get('username'),
        email=data.get('email'),
        password=hashed,
        role=data.get('role', 'client')
    )

    db.session.add(user)
    db.session.commit()

    # Generate token
    token = create_access_token(
        identity=str(user.user_id),
        additional_claims={'role': user.role}
    )

    return jsonify({
        'message': 'Account created successfully',
        'token': token,
        'user': {
            'id': user.user_id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': user.role
        }
    }), 201


def login():
    """Login with email and password."""
    data = request.get_json()

    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    # Find user
    user = User.query.filter_by(email=data.get('email'), is_active=True).first()
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    # Verify password
    if not bcrypt.checkpw(data.get('password').encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Update last login
    user.last_login = db.func.now()
    db.session.commit()

    # Generate token
    token = create_access_token(
        identity=str(user.user_id),
        additional_claims={'role': user.role}
    )

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user.user_id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': user.role
        }
    }), 200


def logout():
    #Logout the current user
    identity = get_jwt_identity()
    return jsonify({
        'message': f'Successfully logged out'
    }), 200