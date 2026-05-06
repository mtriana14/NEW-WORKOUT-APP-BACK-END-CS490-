from app.config.db import db
from app.models import User
from flask import jsonify, Blueprint, request
from sqlalchemy.exc import IntegrityError, DataError

update_user_bp = Blueprint('update_user', __name__)

# update the user taken from the user id based on the fields present
# You can do multiple updates at a time
# STATUS CODES:
# 200: OK, the user was updated
# 400: You provided data for columns not present in the User table
# 404: The user you are trying to edit does not exist in the db 
# 500: Bug in the code, notify Justin!
@update_user_bp.route('/customers/<int:user_id>', methods=["PATCH"])
def update_user(user_id: int):
    """
    Update a user's fields by ID
    ---
    tags:
      - User Management
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          description: Any valid User table fields to update
    responses:
      200:
        description: User updated
      400:
        description: No body or invalid fields
      404:
        description: User not found
      500:
        description: Server error
    """
    body = request.json
    if not body:
        return jsonify({"Failed":"No body"}), 400
    fields = [col.name for col in User.__table__.columns]
    updates = {key: body[key] for key in fields if key in body}
    if len(body) != len(updates):
        return jsonify({"Failed":"Invalid fields present", "Fields":fields}), 400

    query = ", ".join([f"{key} = %s" for key in updates])
    values = list(updates.values())

    conn = db.engine.raw_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user_id FROM Users WHERE user_id=%s
        """, (user_id,))

        if not cursor.fetchone():
            return jsonify({"Failed":"User not found"}), 404

        cursor.execute(
            f"UPDATE Users SET {query}, updated_at = NOW() WHERE user_id = %s",
            values + [user_id]
        )

        conn.commit()
        return jsonify({"Success":"User updated"}), 200

    except Exception as e:
        conn.rollback()
        print(e)
        return jsonify({"Failed":"Some error occured", "Error:":f"{e}"}), 500
    finally:
        if cursor:
            cursor.close()
        conn.close()
