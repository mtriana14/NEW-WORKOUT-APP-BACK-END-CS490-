from flask import request, jsonify
from app.config.db import db
from app.models.user import User
from app.models.coach import Coach
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy.exc import DataError
import bcrypt

def register():
    """
    Register a new user account
    ---
    tags:
      - Authentication
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
          properties:
            first_name:
              type: string
            last_name:
              type: string
            username:
              type: string
            email:
              type: string
            password:
              type: string
            role:
              type: string
              enum: [client, coach]
              default: client
    responses:
      201:
        description: Account created successfully
      400:
        description: Missing required fields
      409:
        description: Email or username already exists
    """
    data = request.get_json()

    # Validate required fields
    if not data.get('first_name') or not data.get('last_name') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'First name, last name, email and password are required'}), 400

    # Check if email already exists
    existing = User.query.filter_by(email=data.get('email')).first()
    if existing:
        return jsonify({'error': 'An account with this email already exists'}), 409
    
    existing = User.query.filter_by(username=data.get('username')).first()
    if existing:
        return jsonify({'error': 'An account with this username already exists'}), 409

    # Hash password
    hashed = bcrypt.hashpw(data.get('password').encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = User(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        username=data.get('username'),
        email=data.get('email'),
        password=hashed,
        role=data.get('role', 'client')
    )

    db.session.add(user)
    db.session.commit()

    # Generate token
    token = create_access_token(
        identity=str(user.user_id),
        additional_claims={'role': user.role}
    )

    return jsonify({
        'message': 'Account created successfully',
        'token': token,
        'user': {
            'id': user.user_id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': user.role
        }
    }), 201


def login():
    """
    Login with email and password
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      400:
        description: Email and password are required
      401:
        description: Invalid email or password
    """
    data = request.get_json()

    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    # Find user
    user = User.query.filter_by(email=data.get('email'), is_active=True).first()
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    # Verify password
    try:
        if not bcrypt.checkpw(data.get('password').encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({'error': 'Invalid email or password'}), 401
    except ValueError: # this is for when the salt is invalid. It resalts the password and reattempts the login
        hashed = bcrypt.hashpw(data.get('password').encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.password = hashed
        login()
    user.last_login = db.func.now()
    db.session.commit()

    # Generate token
    token = create_access_token(
        identity=str(user.user_id),
        additional_claims={'role': user.role}
    )

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user.user_id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': user.role
        }
    }), 200


def logout():
    """
    Logout the current user
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Successfully logged out
    """
    identity = get_jwt_identity()
    return jsonify({
        'message': f'Successfully logged out'
    }), 200

@jwt_required()
def update_user():
    """
    Update the current user's profile
    ---
    tags:
      - User Management
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          description: Dynamic fields from the User model
    responses:
      200:
        description: User updated successfully
      400:
        description: Invalid fields or data error
      404:
        description: User not found
      500:
        description: Server error
    """
    user_id = get_jwt_identity()
    body = request.json
    if not body:
        return jsonify({"Failed":"No body"}), 400
    fields = [col.name for col in User.__table__.columns]
    updates = {key: body[key] for key in fields if key in body}
    if len(body) != len(updates):
        return jsonify({"Failed":"Invalid fields present", "Fields":fields}), 400

    if 'password' in updates:
        hashed = bcrypt.hashpw(updates['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        updates['password'] = hashed

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

@jwt_required()
def update_coach():
    """
    Update coach-specific details
    ---
    tags:
      - User Management
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          description: Dynamic fields from the Coach model
    responses:
      200:
        description: Coach updated successfully
      400:
        description: Invalid fields or data error
      403:
        description: User is not a coach
      404:
        description: Coach record not found
      500:
        description: Server error
    """
    user_id = get_jwt_identity()
    body = request.json
    if not body:
        return jsonify({"Failed":"No body"}), 401
    coach_to_update = User.query.filter_by(user_id = user_id).one()
    if coach_to_update.role != "coach":
        return jsonify({"Failed":"User is not a coach"}), 403
    fields = [col.name for col in Coach.__table__.columns]
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
            SELECT user_id FROM coaches WHERE user_id=%s
        """, (user_id,))

        if not cursor.fetchone():
            return jsonify({"Failed":"User not found"}), 404
        
        cursor.execute(
            f"UPDATE coaches SET {query}, updated_at = NOW() WHERE user_id = %s",
            values + [user_id]
        )

        conn.commit()
        return jsonify({"Success":"Coach Updated"}), 200

    except Exception as e:
            conn.rollback()
            print(e)
            return jsonify({"Failed":"Some error occured", "Error:":f"{e}"}), 500
    except DataError as e:
            conn.rollback()
            print(e)
            return jsonify({"Failed":"Invalid data present"}), 400
    finally:
            if cursor:
                cursor.close()
            conn.close()

@jwt_required()
def delete_user():
    """
    Delete the current user account
    ---
    tags:
      - User Management
    security:
      - Bearer: []
    responses:
      200:
        description: User deleted successfully
      404:
        description: User not found
      500:
        description: Server error
    """
    try:
        user_id = get_jwt_identity()
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