from flask import request, jsonify
from app.config.db import db
from app.models.exercise import Exercise

def get_all_exercises():
    """Get all exercises from the master database."""
    exercises = Exercise.query.filter_by(is_active=True).all()
    result = [
        {
            'id': ex.e_id,
            'name': ex.name,
            'description': ex.description,
            'muscle_group': ex.muscle_group,
            'equipment': ex.equipment,
            'difficulty': ex.difficulty,
            'instructions': ex.instructions,
            'video_url': ex.video_url,
            'created_at': str(ex.created_at)
        }
        for ex in exercises
    ]
    return jsonify({'exercises': result}), 200


def create_exercise():
    """Admin creates a new exercise in the master database."""
    data = request.get_json()

    # Validate required fields
    if not data.get('name') or not data.get('muscle_group'):
        return jsonify({'error': 'Name and muscle group are required'}), 400

    # Check if exercise already exists
    existing = Exercise.query.filter_by(name=data.get('name')).first()
    if existing:
        return jsonify({'error': 'Exercise with this name already exists'}), 409

    exercise = Exercise(
        name=data.get('name'),
        description=data.get('description'),
        muscle_group=data.get('muscle_group'),
        equipment=data.get('equipment', 'bodyweight'),
        difficulty=data.get('difficulty', 'beginner'),
        instructions=data.get('instructions'),
        video_url=data.get('video_url'),
        created_by=data.get('admin_id')
    )

    db.session.add(exercise)
    db.session.commit()
    return jsonify({'message': 'Exercise created successfully', 'id': exercise.id}), 201


def update_exercise(exercise_id):
    """Admin updates an existing exercise."""
    exercise = Exercise.query.filter_by(id=exercise_id, is_active=True).first()
    if not exercise:
        return jsonify({'error': 'Exercise not found'}), 404

    data = request.get_json()

    # Update only provided fields
    if data.get('name'):
        exercise.name = data.get('name')
    if data.get('description'):
        exercise.description = data.get('description')
    if data.get('muscle_group'):
        exercise.muscle_group = data.get('muscle_group')
    if data.get('equipment'):
        exercise.equipment = data.get('equipment')
    if data.get('difficulty'):
        exercise.difficulty = data.get('difficulty')
    if data.get('instructions'):
        exercise.instructions = data.get('instructions')
    if data.get('video_url'):
        exercise.video_url = data.get('video_url')

    db.session.commit()
    return jsonify({'message': 'Exercise updated successfully'}), 200


def delete_exercise(exercise_id):
    """Admin soft deletes an exercise from the master database."""
    exercise = Exercise.query.filter_by(id=exercise_id, is_active=True).first()
    if not exercise:
        return jsonify({'error': 'Exercise not found'}), 404

    # Soft delete - just mark as inactive
    exercise.is_active = False
    db.session.commit()
    return jsonify({'message': 'Exercise deleted successfully'}), 200