from flask import request, jsonify
from app.config.db import db
from app.models.MealPlan import MealPlan
from app.models.coach import Coach
from app.models.user import User
from datetime import datetime


def get_client_meal_plans(user_id, client_id):
    """Get all meal plans for a specific client created by this coach."""
    coach = Coach.query.filter_by(user_id=user_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
    
    plans = MealPlan.query.filter_by(coach_id=coach.coach_id, user_id=client_id).all()
    result = [
        {
            'meal_plan_id': plan.meal_plan_id,
            'user_id': plan.user_id,
            'coach_id': plan.coach_id,
            'name': plan.name,
            'description': plan.description,
            'status': plan.status,
            'created_at': str(plan.created_at),
            'updated_at': str(plan.updated_at)
        }
        for plan in plans
    ]
    return jsonify({'meal_plans': result}), 200


def get_all_coach_meal_plans(user_id):
    """Get all meal plans created by this coach."""
    coach = Coach.query.filter_by(user_id=user_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
    
    plans = MealPlan.query.filter_by(coach_id=coach.coach_id).all()
    result = [
        {
            'meal_plan_id': plan.meal_plan_id,
            'user_id': plan.user_id,
            'client_name': plan.user.first_name if plan.user else None,
            'coach_id': plan.coach_id,
            'name': plan.name,
            'description': plan.description,
            'status': plan.status,
            'created_at': str(plan.created_at),
            'updated_at': str(plan.updated_at)
        }
        for plan in plans
    ]
    return jsonify({'meal_plans': result}), 200


def create_meal_plan(user_id):
    """Create a new meal plan for a client."""
    data = request.get_json()
    
    coach = Coach.query.filter_by(user_id=user_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
    
    client_id = data.get('client_id')
    name = data.get('name')
    description = data.get('description', '')
    
    if not client_id or not name:
        return jsonify({'error': 'client_id and name are required'}), 400
    
    plan = MealPlan(
        user_id=client_id,
        coach_id=coach.coach_id,
        name=name,
        description=description,
        status='active'
    )
    
    db.session.add(plan)
    db.session.commit()
    
    return jsonify({
        'message': 'Meal plan created successfully',
        'meal_plan_id': plan.meal_plan_id
    }), 201


def update_meal_plan(user_id, plan_id):
    """Update an existing meal plan."""
    data = request.get_json()
    
    coach = Coach.query.filter_by(user_id=user_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
    
    plan = MealPlan.query.filter_by(meal_plan_id=plan_id, coach_id=coach.coach_id).first()
    if not plan:
        return jsonify({'error': 'Meal plan not found'}), 404
    
    if 'name' in data:
        plan.name = data['name']
    if 'description' in data:
        plan.description = data['description']
    if 'status' in data:
        plan.status = data['status']
    
    db.session.commit()
    
    return jsonify({'message': 'Meal plan updated successfully'}), 200


def delete_meal_plan(user_id, plan_id):
    """Delete a meal plan."""
    coach = Coach.query.filter_by(user_id=user_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
    
    plan = MealPlan.query.filter_by(meal_plan_id=plan_id, coach_id=coach.coach_id).first()
    if not plan:
        return jsonify({'error': 'Meal plan not found'}), 404
    
    db.session.delete(plan)
    db.session.commit()
    
    return jsonify({'message': 'Meal plan deleted successfully'}), 200