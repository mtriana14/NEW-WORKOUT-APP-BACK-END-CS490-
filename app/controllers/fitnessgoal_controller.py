from flask import request, jsonify
from app.config.db import db
from app.models.fitnessgoals import FitnessGoal
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

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
    try:
        user_id = get_jwt_identity()
        query = FitnessGoal.query.filter_by(user_id = user_id)
        goals = query.order_by(FitnessGoal.created_at.desc()).all()
        return jsonify({"Goals":[goal.to_dict() for goal in goals]}), 200
    except Exception as e:
        print(e)
        return jsonify({"Failed":f"{e}"})
    
@jwt_required()
def edit_fitnessgoal(goal_id):
    user_id = get_jwt_identity()
    data = request.json

    if not data:
        return jsonify({"Failed":"No body present"}), 400
    
    goal = FitnessGoal.query.filter_by(goal_id=goal_id, user_id=user_id).first()

    if not goal:
        return jsonify({"Error":"Goal not found"}), 404
    
    try:
        all_cols = [col.name for col in FitnessGoal.__table__.columns]
        non_edits = ['goal_id', 'user_id', 'created_at', 'updated_at']
        editable = [field for field in all_cols if field not in non_edits]
        updates = {key: data[key] for key in editable if key in data}

        for key, value in updates.items():
            setattr(goal, key, value)

        goal.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({"Success":"Fitnessgoal updated"}), 200
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"Failed":"Some error occured"}), 500
    

