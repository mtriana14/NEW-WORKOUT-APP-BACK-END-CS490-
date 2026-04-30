from app.config.db import db
from app.models import User
from flask import jsonify, Blueprint, request

delete_user_bp = Blueprint('delete_user', __name__)

@delete_user_bp.route('/customers/<int:user_id>', methods=["DELETE"])
def delete_user(user_id):
    """
    Delete a user by ID
    ---
    tags:
      - User Management
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
    responses:
      200:
        description: User deleted
      404:
        description: User not found
      500:
        description: Server error
    """
    try:
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"Failed":"User not found"}), 404
        
        db.session.delete(user)
        db.session.commit()

        return jsonify({"Success":f"{user_id} has been deleted"}), 200
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"Failed":"Some error occured", "Error:":f"{e}"}), 500