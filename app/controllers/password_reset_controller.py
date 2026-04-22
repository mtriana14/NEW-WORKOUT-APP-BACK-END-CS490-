from app.models.user import User
from flask import jsonify, request
from app.config.db import db
from flask_jwt_extended import get_jwt_identity
import bcrypt

# The user forgets their password
def forgot_password_reset():
    try:
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
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"Error":f"{e}"}), 500

# The user simply wants to change thier password
def reset_password():
    try:
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"Error":"No user found"}), 404
        old_pass = request.json.get('old_password')
        if not old_pass:
            return jsonify({"Error":"No password given"}), 400
        if not bcrypt.checkpw(old_pass.encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({'error': 'Invalid password'}), 401
        new_pass = request.json.get('new_password')
        if not new_pass:
            return jsonify({"Error":"No new password given"}), 400
        hashed = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.password = hashed
        db.session.commit()
        return jsonify({"Success":f"Password reset for {user.email}"}), 200
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"Error":f"{e}"}), 500