# DEPRECEATED 
# CREATION OF USER IS INSIDE auth_controller.py

from app.config.db import db
from app.models import User
from flask import jsonify, Blueprint, request
import bcrypt
from sqlalchemy.exc import IntegrityError

create_user_bp = Blueprint('create_user', __name__)

# creates a user with the required fields: first_name, last_name, email, password, and username
# STATUS CODES:
# 201: OK, user was created successfully
# 400: Some of the missing fields were missing
# 500: Some bug in the code, notify Justin!!
@create_user_bp.route('/auth/register', methods=["POST"])
def create_user():
    """
    Register a new user (deprecated — use auth_controller instead)
    ---
    tags:
      - User Management
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - first_name
            - last_name
            - email
            - password
            - username
          properties:
            first_name:
              type: string
            last_name:
              type: string
            email:
              type: string
            password:
              type: string
            username:
              type: string
    responses:
      201:
        description: User created
      400:
        description: Missing fields or duplicate entry
      500:
        description: Server error
    """
    try:
        body = request.json
        required_cols = {'first_name', 'last_name', 'email', 'password', 'username'}
        missing = required_cols - body.keys()

        if missing:
            return jsonify({"Failed":"Missing cols", "Need":list(missing)}), 400

        fields = [col.name for col in User.__table__.columns]
        given = {key: body[key] for key in fields if key in body}

        given['password'] = bcrypt.hashpw(given['password'].encode('utf-8'), bcrypt.gensalt())

        new_user = User(**given)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"Success":"User created"}), 201

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"Failed":"Duplicate entry"}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"Failed":f"{e}"}), 500