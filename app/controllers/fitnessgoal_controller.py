from flask import request, jsonify
from app.config.db import db
from app.models.fitnessgoals import FitnessGoal
from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def create_fitnessgoal():
    user_id = get_jwt_identity()
    data = request.json

    if not data.get('goal_type'):
        return jsonify({'error': 'goal_type is required'}), 400
    try:
        newgoal = FitnessGoal(
            user_id = user_id,
            goal_type = data.get("goal_type"),
            target_value = data.get("target_value"),
            target_unit = data.get("target_unit"),
            deadline = data.get("deadline"),
            status = data.get("status")
        )

        db.session.add(newgoal)
        db.session.commit()
        return jsonify({"Success":"New fitness goal for %s created".format(user_id)}), 201
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"Failed":f"Some error occured {e}"}), 500
    

@jwt_required()
def delete_fitnessgoal(goal_id):
    user_id = get_jwt_identity()
    goal = FitnessGoal.query.filter_by(goal_id = goal_id, user_id = user_id).first()
    if not goal:
        return jsonify({"Failed":"Invalid goal id"}), 404
    
    try:
        db.session.delete(goal)
        db.session.commit()
        return jsonify({"Success":f"Goal {goal_id} has been deleted"}), 200
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"Failed":"Some error has occured"}), 500
    
@jwt_required()
def get_fitnessgoal(goal_id):
    user_id = get_jwt_identity()
    goal = FitnessGoal.query.filter_by(
        goal_id=goal_id,
        user_id=user_id
    ).first()

    if not goal:
        return jsonify({"Failed":"Goal not found"}), 404
    
    return jsonify(goal.to_dict()), 200

@jwt_required()
def get_all_fitnessgoals():
    user_id = get_jwt_identity()
    query = FitnessGoal.query.filter_by(user_id = user_id)
    goals = query.order_by(FitnessGoal.created_at.desc()).all()
    return jsonify({"Goals":[goal.to_dict() for goal in goals]}), 200
