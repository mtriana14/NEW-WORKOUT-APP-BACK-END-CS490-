from flask import request, jsonify
from app.config.db import db
from app.models.user import User
from flask_jwt_extended import create_access_token
import bcrypt

def register():
    """Register a new user account."""
    data = request.get_json()

    # Validate required fields
    if not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Name, email and password are required'}), 400

    # Check if email already exists
    existing = User.query.filter_by(email=data.get('email')).first()
    if existing:
        return jsonify({'error': 'An account with this email already exists'}), 409

    # Hash password
    hashed = bcrypt.hashpw(data.get('password').encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = User(
        name=data.get('name'),
        email=data.get('email'),
        password=hashed,
        role=data.get('role', 'client')
    )

    db.session.add(user)
    db.session.commit()

    # Generate token
    token = create_access_token(identity=str({
        'id': user.user_id,
        'role': user.role
    }))

    return jsonify({
        'message': 'Account created successfully',
        'token': token,
        'user': {
            'id': user.user_id,
            'name': user.first_name,
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

    # Generate token
    token = create_access_token(str({
        'id': user.user_id,
        'role': user.role
    }))

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user.user_id,
            'name': user.first_name,
            'email': user.email,
            'role': user.role
        }
    }), 200