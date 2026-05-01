from app.config.db import db
from app.models import User
from flask import jsonify, Blueprint, request
from sqlalchemy import text

users_bp = Blueprint('users', __name__)

# Simply prints all the users in the Users table
@users_bp.route('/getusers', methods=["GET"])
def get_users():
    conn = db.engine.raw_connection()
    cursor = conn.cursor()
    user_id = request.args.get("user_id")
    try:
        if user_id:
            cursor.execute("SELECT * FROM users u WHERE u.user_id = %s", (user_id))
        else:
            cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        if not users:
            return jsonify({"Error":"No users found"}), 404
        return jsonify(users), 200
    finally:
        cursor.close()
        conn.close()

@users_bp.route('/users/<int:user_id>/name', methods=['GET'])
def get_user_name(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'user_id': user.user_id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': f"{user.first_name} {user.last_name}"
    }), 200
