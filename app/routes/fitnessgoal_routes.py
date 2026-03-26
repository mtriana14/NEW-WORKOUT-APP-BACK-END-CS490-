from flask import Blueprint
from app.controllers.fitnessgoal_controller import create_fitnessgoal, delete_fitnessgoal, get_fitnessgoal, get_all_fitnessgoals

fitnessgoal_bp = Blueprint('fitnessgoals', __name__)

fitnessgoal_bp.route('/fitnessgoal', methods=["POST"])(create_fitnessgoal)
fitnessgoal_bp.route('/fitnessgoal/<int:goal_id>', methods=["DELETE"])(delete_fitnessgoal)
fitnessgoal_bp.route('/fitnessgoal/<int:goal_id>', methods=["GET"])(get_fitnessgoal)
fitnessgoal_bp.route('/fitnessgoal', methods=["GET"])(get_all_fitnessgoals)