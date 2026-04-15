from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.controllers.user_controller import get_all_users

user_bp = Blueprint('users', __name__)

@user_bp.route('/users', methods=['GET'])
 
def list_users():
    return get_all_users()