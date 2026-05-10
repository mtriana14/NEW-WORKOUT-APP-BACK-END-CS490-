from flask import request, jsonify
from app.config.db import db
from app.models.exercise import Exercise


def _exercise_dict(ex):
    return {
        'id': ex.e_id,
        'e_id': ex.e_id,
        'name': ex.name,
        'description': ex.description,
        'muscle_group': ex.muscle_group,
        'equipment_type': ex.equipment_type,
        'difficulty': ex.difficulty,
        'instructions': ex.instructions,
        'video_url': ex.video_url,
        'is_active': ex.is_active,
        'created_at': ex.created_at.isoformat() if ex.created_at else None,
        'updated_at': ex.updated_at.isoformat() if ex.updated_at else None,
    }


def get_all_exercises():
    """
    Get all active exercises
    ---
    tags:
      - Exercises
    security:
      - Bearer: []
    responses:
      200:
        description: List of exercises
    """
    exercises = Exercise.query.filter_by(is_active=True).all()
    return jsonify({'exercises': [_exercise_dict(ex) for ex in exercises]}), 200


def get_exercise_by_id(exercise_id):
    """
    Get a single exercise by ID
    ---
    tags:
      - Exercises
    security:
      - Bearer: []
    parameters:
      - in: path
        name: exercise_id
        type: integer
        required: true
    responses:
      200:
        description: Exercise details
      404:
        description: Exercise not found
    """
    exercise = Exercise.query.filter_by(e_id=exercise_id, is_active=True).first()
    if not exercise:
        return jsonify({'error': 'Exercise not found'}), 404
    return jsonify({'exercise': _exercise_dict(exercise)}), 200


def create_exercise():
    """
    Create a new exercise (admin)
    ---
    tags:
      - Exercises
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - muscle_group
          properties:
            name:
              type: string
            description:
              type: string
            muscle_group:
              type: string
            equipment_type:
              type: string
            difficulty:
              type: string
              enum: [beginner, intermediate, advanced]
            instructions:
              type: string
            video_url:
              type: string
    responses:
      201:
        description: Exercise created
      400:
        description: Missing required fields
      409:
        description: Exercise name already exists
    """
    data = request.get_json() or {}

    if not data.get('name') or not data.get('muscle_group'):
        return jsonify({'error': 'Name and muscle group are required'}), 400

    if Exercise.query.filter_by(name=data.get('name')).first():
        return jsonify({'error': 'Exercise with this name already exists'}), 409

    exercise = Exercise(
        name=data.get('name'),
        description=data.get('description'),
        muscle_group=data.get('muscle_group'),
        equipment_type=data.get('equipment_type', 'bodyweight'),
        difficulty=data.get('difficulty', 'beginner'),
        instructions=data.get('instructions'),
        video_url=data.get('video_url'),
        created_by=data.get('admin_id'),
    )
    db.session.add(exercise)
    db.session.commit()
    return jsonify({'message': 'Exercise created successfully', 'exercise': _exercise_dict(exercise)}), 201


def update_exercise(exercise_id):
    """
    Update an exercise (admin)
    ---
    tags:
      - Exercises
    security:
      - Bearer: []
    parameters:
      - in: path
        name: exercise_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
            muscle_group:
              type: string
            equipment_type:
              type: string
            difficulty:
              type: string
            instructions:
              type: string
            video_url:
              type: string
    responses:
      200:
        description: Exercise updated
      404:
        description: Exercise not found
    """
    exercise = Exercise.query.filter_by(e_id=exercise_id, is_active=True).first()
    if not exercise:
        return jsonify({'error': 'Exercise not found'}), 404

    data = request.get_json() or {}
    if data.get('name'):
        exercise.name = data['name']
    if data.get('description') is not None:
        exercise.description = data['description']
    if data.get('muscle_group'):
        exercise.muscle_group = data['muscle_group']
    if data.get('equipment_type'):
        exercise.equipment_type = data['equipment_type']
    if data.get('difficulty'):
        exercise.difficulty = data['difficulty']
    if data.get('instructions') is not None:
        exercise.instructions = data['instructions']
    if data.get('video_url') is not None:
        exercise.video_url = data['video_url']

    db.session.commit()
    return jsonify({'message': 'Exercise updated successfully', 'exercise': _exercise_dict(exercise)}), 200


def delete_exercise(exercise_id):
    """
    Soft-delete an exercise (admin)
    ---
    tags:
      - Exercises
    security:
      - Bearer: []
    parameters:
      - in: path
        name: exercise_id
        type: integer
        required: true
    responses:
      200:
        description: Exercise deleted
      404:
        description: Exercise not found
    """
    exercise = Exercise.query.filter_by(e_id=exercise_id, is_active=True).first()
    if not exercise:
        return jsonify({'error': 'Exercise not found'}), 404

    exercise.is_active = False
    db.session.commit()
    return jsonify({'message': 'Exercise deleted successfully'}), 200


_COMMON_EXERCISES = [
    {'name': 'Barbell Squat', 'muscle_group': 'legs', 'equipment_type': 'barbell', 'difficulty': 'intermediate', 'description': 'A compound lower-body exercise.', 'instructions': 'Stand with feet shoulder-width apart, bar on upper back. Squat down until thighs are parallel to floor, then drive back up.'},
    {'name': 'Bench Press', 'muscle_group': 'chest', 'equipment_type': 'barbell', 'difficulty': 'intermediate', 'description': 'A compound upper-body pushing exercise.', 'instructions': 'Lie on bench, grip bar slightly wider than shoulder-width. Lower to chest then press back up.'},
    {'name': 'Deadlift', 'muscle_group': 'back', 'equipment_type': 'barbell', 'difficulty': 'intermediate', 'description': 'A full-body compound pulling exercise.', 'instructions': 'Stand over bar, hinge at hips, grip bar. Drive through heels and lock out hips and knees at top.'},
    {'name': 'Pull-Up', 'muscle_group': 'back', 'equipment_type': 'bodyweight', 'difficulty': 'intermediate', 'description': 'An upper-body pulling exercise using bodyweight.', 'instructions': 'Hang from bar with overhand grip. Pull chest to bar, then lower with control.'},
    {'name': 'Push-Up', 'muscle_group': 'chest', 'equipment_type': 'bodyweight', 'difficulty': 'beginner', 'description': 'A foundational upper-body pushing exercise.', 'instructions': 'Start in plank position, lower chest to ground, then push back up.'},
    {'name': 'Dumbbell Lunges', 'muscle_group': 'legs', 'equipment_type': 'dumbbell', 'difficulty': 'beginner', 'description': 'A unilateral lower-body exercise.', 'instructions': 'Hold dumbbells at sides, step forward and lower back knee toward floor, then return.'},
    {'name': 'Overhead Press', 'muscle_group': 'shoulders', 'equipment_type': 'barbell', 'difficulty': 'intermediate', 'description': 'A compound shoulder pressing movement.', 'instructions': 'Hold bar at shoulder height, press overhead until arms are fully extended.'},
    {'name': 'Dumbbell Curl', 'muscle_group': 'arms', 'equipment_type': 'dumbbell', 'difficulty': 'beginner', 'description': 'An isolation exercise for the biceps.', 'instructions': 'Hold dumbbells at sides, curl up while keeping elbows fixed, then lower.'},
    {'name': 'Tricep Dip', 'muscle_group': 'arms', 'equipment_type': 'bodyweight', 'difficulty': 'beginner', 'description': 'A bodyweight tricep exercise.', 'instructions': 'Grip bars or bench edge, lower body by bending elbows, then press back up.'},
    {'name': 'Plank', 'muscle_group': 'core', 'equipment_type': 'bodyweight', 'difficulty': 'beginner', 'description': 'An isometric core stability exercise.', 'instructions': 'Hold a straight-body position on forearms and toes. Keep hips level and breathe steadily.'},
    {'name': 'Romanian Deadlift', 'muscle_group': 'glutes', 'equipment_type': 'barbell', 'difficulty': 'intermediate', 'description': 'A hip-hinge movement targeting hamstrings and glutes.', 'instructions': 'Hold bar at hips, hinge forward keeping back flat until hamstrings are stretched, then return.'},
    {'name': 'Cable Row', 'muscle_group': 'back', 'equipment_type': 'cables', 'difficulty': 'beginner', 'description': 'A horizontal pulling exercise for the mid-back.', 'instructions': 'Sit at cable machine, pull handle to abdomen keeping elbows close, then return.'},
    {'name': 'Leg Press', 'muscle_group': 'legs', 'equipment_type': 'machine', 'difficulty': 'beginner', 'description': 'A machine-based lower-body pushing exercise.', 'instructions': 'Sit in machine, place feet on platform. Lower platform toward chest then press back out.'},
    {'name': 'Lateral Raise', 'muscle_group': 'shoulders', 'equipment_type': 'dumbbell', 'difficulty': 'beginner', 'description': 'An isolation exercise for the lateral deltoid.', 'instructions': 'Hold dumbbells at sides, raise arms out to shoulder height then lower.'},
    {'name': 'Russian Twist', 'muscle_group': 'core', 'equipment_type': 'bodyweight', 'difficulty': 'beginner', 'description': 'A rotational core exercise.', 'instructions': 'Sit with knees bent and feet lifted, rotate torso side to side tapping the floor.'},
]


def bulk_create_common_exercises():
    """
    Bulk-create a set of common exercises (admin)
    ---
    tags:
      - Exercises
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            exercises:
              type: array
              description: Custom list; omit to seed the built-in 15 common exercises
              items:
                type: object
    responses:
      201:
        description: Exercises created (skipped duplicates reported)
      400:
        description: Empty exercises array provided
    """
    data = request.get_json(silent=True, force=True) or {}
    exercises_input = data.get('exercises')

    exercises_to_create = exercises_input if exercises_input else _COMMON_EXERCISES

    if not exercises_to_create:
        return jsonify({'error': 'exercises array is required and must not be empty'}), 400

    created = []
    skipped = 0

    for item in exercises_to_create:
        if not item.get('name'):
            skipped += 1
            continue
        if Exercise.query.filter_by(name=item['name']).first():
            skipped += 1
            continue

        exercise = Exercise(
            name=item.get('name'),
            description=item.get('description'),
            muscle_group=item.get('muscle_group'),
            equipment_type=item.get('equipment_type', 'bodyweight'),
            difficulty=item.get('difficulty', 'beginner'),
            instructions=item.get('instructions'),
        )
        db.session.add(exercise)
        created.append(exercise)

    db.session.commit()

    return jsonify({
        'message': f'{len(created)} exercise(s) created successfully',
        'created_count': len(created),
        'skipped_count': skipped,
        'exercises': [_exercise_dict(ex) for ex in created],
    }), 201
