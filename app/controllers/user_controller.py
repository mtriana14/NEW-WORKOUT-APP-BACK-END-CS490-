from flask import jsonify
from flask_jwt_extended import jwt_required
from app.models import User

def get_all_users():
    users = User.query.all()
        
    return jsonify([{
        "id":         u.user_id,
        "first_name": u.first_name,
        "last_name":  u.last_name,
        "email":      u.email,
        "role":       u.role,
        "is_active":  u.is_active,
        "created_at": u.created_at.isoformat() if u.created_at else None,
    } for u in users])