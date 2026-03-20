from app.config.db import db
from app.models import User
from flask import jsonify, Blueprint
from sqlalchemy import text

users_bp = Blueprint('users', __name__)

@users_bp.route('/getusers', methods=["GET"])
def get_users():
    conn = db.engine.raw_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        if users is None:
            return jsonify({"Error":"No users in db"}), 404
        return jsonify(users), 200
    finally:
        cursor.close()
        conn.close()
