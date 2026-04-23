from flask import request, jsonify
from app.config.db import db
from app.models.user import User
from datetime import datetime


def get_all_users():
    """
    GET /api/admin/users?role=client|coach|admin
    Returns all users with counts broken down by role.
    """
    role_filter = request.args.get('role')

    query = User.query
    if role_filter and role_filter != 'all':
        query = query.filter_by(role=role_filter)

    users = query.order_by(User.created_at.desc()).all()

    # Counts always across ALL users regardless of filter
    total      = User.query.count()
    clients    = User.query.filter_by(role='client').count()
    coaches    = User.query.filter_by(role='coach').count()
    admins     = User.query.filter_by(role='admin').count()
    active     = User.query.filter_by(is_active=True).count()

    return jsonify({
        'users': [
            {
                'user_id':    u.user_id,
                'name':       f'{u.first_name} {u.last_name}',
                'first_name': u.first_name,
                'last_name':  u.last_name,
                'email':      u.email,
                'role':       u.role,
                'is_active':  u.is_active,
                'phone':      u.phone,
                'last_login': u.last_login.isoformat() if u.last_login else None,
                'created_at': u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
        'counts': {
            'total':   total,
            'clients': clients,
            'coaches': coaches,
            'admins':  admins,
            'active':  active,
        }
    }), 200


def update_user_status(user_id):
    """
    PUT /api/admin/users/<user_id>/status
    Body: { is_active: true|false }
    Toggles a user's active status.
    """
    data = request.get_json() or {}

    if 'is_active' not in data:
        return jsonify({'error': 'is_active is required'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.is_active = bool(data['is_active'])
    user.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': f"User {'activated' if user.is_active else 'deactivated'} successfully",
        'user': {
            'user_id':   user.user_id,
            'name':      f'{user.first_name} {user.last_name}',
            'first_name': user.first_name,
            'last_name':  user.last_name,
            'email':     user.email,
            'role':      user.role,
            'is_active': user.is_active,
        }
    }), 200