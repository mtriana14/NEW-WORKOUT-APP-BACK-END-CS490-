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


