from flask import request, jsonify, current_app
from app.config.db import db
from app.models.user import User
from flask_jwt_extended import create_access_token
import os
import secrets
import bcrypt


def google_sign_in():
    """
    Frontend sends Google's ID token after the user completes Google's popup.
    We verify it with Google, then either create a new User or log in the
    existing one. Returns the same token+user shape as /auth/login.
    """
    data = request.get_json() or {}
    id_token_str = data.get('id_token') or data.get('credential')

    if not id_token_str:
        return jsonify({'error': 'Google id_token is required'}), 400

    client_id = os.getenv('GOOGLE_CLIENT_ID')
    if not client_id:
        return jsonify({'error': 'Google OAuth is not configured on the server'}), 500

    try:
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests
    except ImportError:
        return jsonify({
            'error': 'google-auth is not installed. Run: pip install google-auth'
        }), 500

    # Verify the token with Google
    try:
        idinfo = google_id_token.verify_oauth2_token(
            id_token_str,
            google_requests.Request(),
            client_id
        )
    except ValueError as e:
        return jsonify({'error': f'Invalid Google token: {e}'}), 401

    email       = idinfo.get('email')
    first_name  = idinfo.get('given_name') or 'Google'
    last_name   = idinfo.get('family_name') or 'User'
    picture     = idinfo.get('picture')
    email_verified = idinfo.get('email_verified', False)

    if not email:
        return jsonify({'error': 'Google account has no email'}), 400
    if not email_verified:
        return jsonify({'error': 'Google email is not verified'}), 403

    user = User.query.filter_by(email=email).first()
    created = False

    if not user:
        # Create new account. we store a random 
        # unusable one to satisfy the NOT NULL constraint if present.
        random_pw = bcrypt.hashpw(
            secrets.token_urlsafe(32).encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')

        # Build a unique username from the email local part
        base_username = email.split('@')[0][:50]
        candidate = base_username
        suffix = 0
        while User.query.filter_by(username=candidate).first():
            suffix += 1
            candidate = f'{base_username}{suffix}'[:100]

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=candidate,
            email=email,
            password=random_pw,
            role='client',
            profile_photo=picture,
        )
        db.session.add(user)
        db.session.commit()
        created = True

    user.last_login = db.func.now()
    db.session.commit()

    token = create_access_token(
        identity=str(user.user_id),
        additional_claims={'role': user.role}
    )

    return jsonify({
        'message': 'Google sign-in successful' if not created else 'Account created via Google',
        'created': created,
        'token': token,
        'user': {
            'id':         user.user_id,
            'first_name': user.first_name,
            'last_name':  user.last_name,
            'email':      user.email,
            'role':       user.role,
        }
    }), 200
