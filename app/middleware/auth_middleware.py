from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

def login_required(f):
    """Verify that the request has a valid JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception as e:
            print(f"JWT ERROR: {e}")
            return jsonify({'error': 'Unauthorized - valid token required'}), 401
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Verify that the logged in user is an admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('role') != 'admin':
                return jsonify({'error': 'Forbidden - admin access required'}), 403
        except Exception as e:
            print(f"JWT ERROR: {e}")
            return jsonify({'error': 'Unauthorized - valid token required'}), 401
        return f(*args, **kwargs)
    return decorated


def coach_required(f):
    """Verify that the logged in user is a coach."""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('role') != 'coach':
                return jsonify({'error': 'Forbidden - coach access required'}), 403
        except Exception as e:
            print(f"JWT ERROR: {e}")
            return jsonify({'error': 'Unauthorized - valid token required'}), 401
        return f(*args, **kwargs)
    return decorated



def coach_or_admin_required(f):
    """Verify that the logged in user is a coach or admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('role') not in ['coach', 'admin']:
                return jsonify({'error': 'Forbidden - coach or admin access required'}), 403
        except Exception as e:
            print(f"JWT ERROR: {e}")
            return jsonify({'error': 'Unauthorized - valid token required'}), 401
        return f(*args, **kwargs)
    return decorated