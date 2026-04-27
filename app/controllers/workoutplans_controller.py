from flask import request, jsonify
from app.config.db import db
from app.models.WorkoutPlan import WorkoutPlan
from app.models.coach import Coach
from app.models.user import User
from datetime import datetime


def get_client_workout_plans(user_id, client_id):
    """Get all workout plans for a specific client created by this coach."""
    coach = Coach.query.filter_by(user_id=user_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
    
    plans = WorkoutPlan.query.filter_by(coach_id=coach.coach_id, user_id=client_id).all()
    result = [
        {
            'plan_id': plan.plan_id,
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
    return jsonify({'workout_plans': result}), 200


def get_all_coach_workout_plans(user_id):
    """Get all workout plans created by this coach."""
    coach = Coach.query.filter_by(user_id=user_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
    
    plans = WorkoutPlan.query.filter_by(coach_id=coach.coach_id).all()
    result = [
        {
            'plan_id': plan.plan_id,
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
    return jsonify({'workout_plans': result}), 200


def create_workout_plan(user_id):
    """Create a workout plan — works for both coaches and clients."""
    from flask_jwt_extended import get_jwt_identity
    data = request.get_json() or {}
    jwt_user_id = int(get_jwt_identity())

    name = data.get('name')
    if not name:
        return jsonify({'error': 'name is required'}), 400

    coach = Coach.query.filter_by(user_id=jwt_user_id).first()

    if coach:
        # Coach creating plan for a client
        client_id = data.get('client_id')
        if not client_id:
            return jsonify({'error': 'client_id is required for coaches'}), 400
        plan_user_id = client_id
        plan_coach_id = coach.coach_id
    else:
        # Client creating their own plan
        plan_user_id = jwt_user_id
        plan_coach_id = None

    plan = WorkoutPlan(
        user_id=plan_user_id,
        coach_id=plan_coach_id,
        name=name,
        description=data.get('description', ''),
        status='active'
    )
    db.session.add(plan)
    db.session.commit()

    return jsonify({
        'message': 'Workout plan created successfully',
        'plan_id': plan.plan_id
    }), 201


def update_workout_plan(user_id, plan_id):
    """Update an existing workout plan."""
    data = request.get_json()
    
    coach = Coach.query.filter_by(user_id=user_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
    
    plan = WorkoutPlan.query.filter_by(plan_id=plan_id, coach_id=coach.coach_id).first()
    if not plan:
        return jsonify({'error': 'Workout plan not found'}), 404
    
    if 'name' in data:
        plan.name = data['name']
    if 'description' in data:
        plan.description = data['description']
    if 'status' in data:
        plan.status = data['status']
    
    db.session.commit()
    
    return jsonify({'message': 'Workout plan updated successfully'}), 200


def delete_workout_plan(user_id, plan_id):
    """Delete a workout plan."""
    coach = Coach.query.filter_by(user_id=user_id).first()
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
    
    plan = WorkoutPlan.query.filter_by(plan_id=plan_id, coach_id=coach.coach_id).first()
    if not plan:
        return jsonify({'error': 'Workout plan not found'}), 404
    
    db.session.delete(plan)
    db.session.commit()
    
    return jsonify({'message': 'Workout plan deleted successfully'}), 200

def get_my_workout_plans():
    """Client gets all their own workout plans."""
    from flask_jwt_extended import get_jwt_identity
    user_id = int(get_jwt_identity())
    plans = WorkoutPlan.query.filter_by(user_id=user_id).all()
    result = [
        {
            'plan_id': p.plan_id,
            'name': p.name,
            'description': p.description,
            'status': p.status,
            'coach_id': p.coach_id,
            'created_at': str(p.created_at),
            'updated_at': str(p.updated_at)
        }
        for p in plans
    ]
    return jsonify({'workout_plans': result}), 200