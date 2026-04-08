from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.config.db import db
from app.models.meal_plan import MealPlan
from datetime import datetime

@jwt_required()
def create_mealplan():
    try:
        user_id = get_jwt_identity()
        data = request.json
        if not data:
            return jsonify({"Error":"No body"}), 400
        
        mealplan = MealPlan (
            user_id = user_id,
            coach_id = data.get("coach_id"),
            name = data.get("name"),
            description = data.get("description"),
            status = data.get("status")
        )

        db.session.add(mealplan)
        db.session.commit()
        return jsonify({"Success":"Mealplan created", "Description":f"{data.get("description")}"}), 200

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"Failed":"Some error occured", "Details":f"{e}"}), 500
    
@jwt_required()
def delete_mealplan(mealplan_id):
    try:
        user_id = get_jwt_identity()
        mealplan = MealPlan.query.filter_by(meal_plan_id = mealplan_id, user_id = user_id).first()
        if not mealplan:
            return jsonify({"Failed":"No mealplan found"}), 404
        db.session.delete(mealplan)
        db.session.commit()
        return jsonify({"Success":f"Mealplan {mealplan_id} deleted"}), 200
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"Failed":f"Details: {e}"}), 500
    
@jwt_required()
def update_mealplan(mealplan_id):
    try:
        user_id = get_jwt_identity()
        data = request.json

        if not data:
            return jsonify({"Failed":"No body"}), 400
        
        mealplan = MealPlan.query.filter_by(meal_plan_id = mealplan_id, user_id = user_id).first()

        if not mealplan:
            return jsonify({"Failed":"No mealplan found"}), 404

        all_cols = [col.name for col in MealPlan.__table__.columns]
        non_edits = ['mealplan_id', 'user_id', 'created_at', 'updated_at']
        editable = [field for field in all_cols if field not in non_edits]
        updates = {key: data[key] for key in editable if key in data}

        for key, value in updates.items():
            setattr(mealplan, key, value)

        mealplan.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({"Success":f"Mealplan {mealplan_id} has been updated"}), 200

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"Failed":f"Details: {e}"}), 500
    
@jwt_required()
def get_one_mealplan(mealplan_id):
    try:
        user_id = get_jwt_identity()
        mealplan = MealPlan.query.filter_by(meal_plan_id = mealplan_id, user_id = user_id).first()

        if not mealplan:
            return jsonify({"Failed":"Mealplan not found"}), 404
        
        return jsonify(mealplan.to_dict()), 200
    except Exception as e:
        print(e)
        return jsonify({"Failed":f"Details: {e}"}), 500
    
@jwt_required()
def get_all_mealplans():
    try:
        user_id = get_jwt_identity()
        query = MealPlan.query.filter_by(user_id = user_id)
        mealplans = query.order_by(MealPlan.created_at.desc()).all()
        return jsonify({"Mealplans":[mealplan.to_dict() for mealplan in mealplans]}), 200
    except Exception as e:
        print(e)
        return jsonify({"Failed":f"Details: {e}"}), 500
    
