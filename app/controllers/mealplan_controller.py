from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.config.db import db
from app.models.meal_plan import MealPlan
from app.models.MealPlanFood import MealPlanFood
from app.models.coach import Coach
from app.models.user import User
from datetime import datetime

@jwt_required()
def create_mealplan():
    try:
        user_id = get_jwt_identity()
        data = request.json
        if not data:
            return jsonify({"Error":"No body"}), 400

        if "name" not in data:
            return jsonify({"Failed":"Missing data"}), 400
        
        mealplan = MealPlan (
            user_id = user_id,
            coach_id = data.get("coach_id"),
            name = data.get("name"),
            description = data.get("description"),
            status = data.get("status")
        )

        db.session.add(mealplan)
        db.session.commit()
        return jsonify({"Success":"Mealplan created", "Description":f"{data.get("description")}"}), 201

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

        if len(updates) == 0:
            return jsonify({"Error":"No real data"}), 400

        for key, value in updates.items():
            setattr(mealplan, key, value)

        mealplan.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({"Success":f"Mealplan {mealplan_id} has been updated",
                        "name":f"{mealplan.name}",
                        "description":f"{mealplan.description}",
                        "updated_at":f"{datetime.utcnow()}"}), 200

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
    
def _plan_with_days(plan):
    """Helper — returns a meal plan dict with food items grouped by day."""
    coach      = Coach.query.get(plan.coach_id) if plan.coach_id else None
    coach_user = User.query.get(coach.user_id) if coach else None
    coach_name = f"{coach_user.first_name} {coach_user.last_name}" if coach_user else None

    # Group food items by day
    days_map = {}
    for item in plan.food_items:
        day = item.day_of_week
        if day not in days_map:
            days_map[day] = []
        days_map[day].append({
            'id':           item.item_id,
            'name':         item.meal_type.capitalize(),
            'details':      f"{item.food_name}{' — ' + item.portion_size if item.portion_size else ''}",
            'calories':     item.calories or 0,
            'completed':    False,  # no completed column in schema
            'protein':      float(item.protein) if item.protein else None,
            'carbs':        float(item.carbs) if item.carbs else None,
            'fat':          float(item.fat) if item.fat else None,
        })

    # Sort days in week order
    day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    days = [
        {'day': d, 'meals': days_map[d]}
        for d in day_order if d in days_map
    ]

    return {
        'meal_plan_id': plan.meal_plan_id,
        'id':           plan.meal_plan_id,   # frontend expects 'id'
        'title':        plan.name,           # frontend expects 'title'
        'name':         plan.name,
        'description':  plan.description,
        'coach':        coach_name,          # frontend expects 'coach'
        'coach_name':   coach_name,
        'status':       plan.status,
        'days':         days,
        'created_at':   plan.created_at.isoformat() if plan.created_at else None,
        'updated_at':   plan.updated_at.isoformat() if plan.updated_at else None,
    }


@jwt_required()
def add_food_item(mealplan_id):
    try:
        user_id = get_jwt_identity()

        mealplan = MealPlan.query.filter_by(meal_plan_id=mealplan_id, user_id=user_id).first()
        if not mealplan:
            return jsonify({"Failed": "Mealplan not found"}), 404

        data = request.json or {}
        if not data.get('day_of_week') or not data.get('meal_type') or not data.get('food_name'):
            return jsonify({"Failed": "day_of_week, meal_type, and food_name are required"}), 400

        item = MealPlanFood(
            meal_plan_id = mealplan_id,
            day_of_week  = data.get('day_of_week'),
            meal_type    = data.get('meal_type'),
            food_name    = data.get('food_name'),
            calories     = data.get('calories'),
            protein      = data.get('protein'),
            carbs        = data.get('carbs'),
            fat          = data.get('fat'),
            portion_size = data.get('portion_size'),
            notes        = data.get('notes'),
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({"Success": "Food item added", "item_id": item.item_id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"Failed": f"{e}"}), 500