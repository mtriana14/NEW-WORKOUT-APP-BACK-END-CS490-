from app.config.db import db
from app.models import User
from flask import jsonify, Blueprint, request
from sqlalchemy import text

update_user_bp = Blueprint('update_user', __name__)

# update the user taken from the user id based on the fields present
@update_user_bp.route('/customers/<int:user_id>', methods=["PATCH"])
def update_user(user_id: int):
        body = request.json
        if not body:
            return jsonify({"Failed":"No body"}), 400
        fields = [col.name for col in User.__table__.columns]
        updates= {key: body[key] for key in fields if key in body}
        if len(body) != len(updates):
            return jsonify({"Failed":"Invalid fields present", "Fields":fields}), 400
        
        query = ", ".join([f"{key} = %s" for key in updates])
        values = list(updates.values())
        
        conn = db.engine.raw_connection()
        cursor = None
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT user_id FROM users WHERE user_id=%s
            """, (user_id,))

            if not cursor.fetchone():
                return jsonify({"Failed":"User not found"}), 404
            
            cursor.execute(
                f"UPDATE users SET {query}, updated_at = NOW() WHERE user_id = %s",
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
