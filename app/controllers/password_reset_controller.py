from app.models.user import User
from flask import jsonify, request
from app.config.db import db
from flask_jwt_extended import get_jwt_identity
import bcrypt

def forgot_password_reset():
    """
    Reset password by email (no token required)
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
              description: The new password to set
    responses:
      200:
        description: Password reset successfully
      400:
        description: Missing email or password
      404:
        description: No account with that email
    """
    email = request.json.get('email')
    password = request.json.get('password')
    if not email or not password:
        return jsonify({"Failed":"Missing email or pass"}), 400
    user = User.query.filter_by(email = email).first()
    if not user:
        return jsonify({"Failed":"No such email exists"}), 404
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user.password = hashed
    db.session.commit()
    return jsonify({"Success":f"Password reset for {email}"}), 200

def reset_password():
    """
    Change password while logged in
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - old_password
            - new_password
          properties:
            old_password:
              type: string
            new_password:
              type: string
    responses:
      200:
        description: Password changed successfully
      401:
        description: Old password is incorrect
    """
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    old_pass = request.json.get('old_password')
    if not bcrypt.checkpw(old_pass.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'error': 'Invalid password'}), 401
    new_pass = request.json.get('new_password')
    hashed = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user.password = hashed
    db.session.commit()
    return jsonify({"Success":f"Password reset for {user.email}"}), 200

    
    