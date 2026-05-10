import os
from datetime import datetime
from flask import request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity, get_jwt
from werkzeug.utils import secure_filename

from app.config.db import db
from app.models.progress_photo import ProgressPhoto
from app.models.coach import Coach
from app.models.hire import Hire


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
VALID_LABELS = {'before', 'progress', 'after'}


def _allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_progress_photo():
    """
    Upload a progress photo
    ---
    tags:
      - Progress Photos
    security:
      - Bearer: []
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: photo
        type: file
        required: true
      - in: formData
        name: label
        type: string
        enum: [before, progress, after]
        default: progress
      - in: formData
        name: caption
        type: string
      - in: formData
        name: weight
        type: number
      - in: formData
        name: taken_on
        type: string
        description: YYYY-MM-DD
    responses:
      201:
        description: Photo uploaded
      400:
        description: Missing file or invalid label/date
    """
    try:
        user_id = int(get_jwt_identity())
        if 'photo' not in request.files:
            return jsonify({'error': 'No file in the request (field name must be "photo")'}), 400

        file = request.files['photo']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        if not _allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        label = (request.form.get('label') or 'progress').lower()
        if label not in VALID_LABELS:
            return jsonify({'error': f'label must be one of {sorted(VALID_LABELS)}'}), 400

        caption = request.form.get('caption')
        weight = request.form.get('weight')
        taken_on_str = request.form.get('taken_on')

        taken_on = None
        if taken_on_str:
            try:
                taken_on = datetime.strptime(taken_on_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'taken_on must be YYYY-MM-DD'}), 400

        filename = secure_filename(file.filename)
        ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_filename = f'user_{user_id}_{label}_{ts}_{filename}'

        upload_folder = current_app.config.get(
            'PROGRESS_PHOTO_FOLDER', 'static/uploads/progress_photos'
        )
        os.makedirs(upload_folder, exist_ok=True)
        fs_path = os.path.join(upload_folder, unique_filename)
        file.save(fs_path)

        db_path = f'/static/uploads/progress_photos/{unique_filename}'

        photo = ProgressPhoto(
            user_id=user_id,
            file_path=db_path,
            label=label,
            caption=caption,
            weight_at_time=float(weight) if weight else None,
            taken_on=taken_on,
        )
        db.session.add(photo)
        db.session.commit()

        return jsonify({
            'message': 'Progress photo uploaded',
            'photo':   photo.to_dict(),
        }), 201

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'error': f'{e}'}), 500


def list_my_progress_photos():
    """
    Get your own progress photos
    ---
    tags:
      - Progress Photos
    security:
      - Bearer: []
    parameters:
      - in: query
        name: label
        type: string
        enum: [before, progress, after]
    responses:
      200:
        description: List of progress photos
    """
    user_id = int(get_jwt_identity())
    label = request.args.get('label')

    query = ProgressPhoto.query.filter_by(user_id=user_id, is_deleted=False)
    if label:
        if label not in VALID_LABELS:
            return jsonify({'error': f'label must be one of {sorted(VALID_LABELS)}'}), 400
        query = query.filter_by(label=label)

    photos = query.order_by(
        ProgressPhoto.taken_on.desc(),
        ProgressPhoto.created_at.desc()
    ).all()

    return jsonify({
        'total':  len(photos),
        'photos': [p.to_dict() for p in photos],
    }), 200


def get_client_progress_photos(client_id):
    """
    Get a client's progress photos (coach only)
    ---
    tags:
      - Progress Photos
    security:
      - Bearer: []
    parameters:
      - in: path
        name: client_id
        type: integer
        required: true
    responses:
      200:
        description: Client's progress photos
      403:
        description: Not a coach or client not assigned to you
      404:
        description: Coach profile not found
    """
    user_id = int(get_jwt_identity())
    role = get_jwt().get('role')

    if role != 'coach':
        return jsonify({'error': 'Forbidden - coach access required'}), 403

    coach = Coach.query.filter_by(user_id=user_id).first()
    if not coach:
        return jsonify({'error': 'Coach profile not found'}), 404

    hire = Hire.query.filter_by(
        user_id=client_id, coach_id=coach.coach_id, status='active'
    ).first()
    if not hire:
        return jsonify({'error': 'That client is not assigned to you'}), 403

    photos = (
        ProgressPhoto.query.filter_by(user_id=client_id, is_deleted=False)
        .order_by(ProgressPhoto.taken_on.desc(),
                  ProgressPhoto.created_at.desc())
        .all()
    )
    return jsonify({
        'client_id': client_id,
        'total':     len(photos),
        'photos':    [p.to_dict() for p in photos],
    }), 200


def delete_progress_photo(photo_id):
    """
    Delete a progress photo
    ---
    tags:
      - Progress Photos
    security:
      - Bearer: []
    parameters:
      - in: path
        name: photo_id
        type: integer
        required: true
    responses:
      200:
        description: Photo deleted
      404:
        description: Photo not found
    """
    user_id = int(get_jwt_identity())

    photo = ProgressPhoto.query.filter_by(
        photo_id=photo_id, user_id=user_id, is_deleted=False
    ).first()
    if not photo:
        return jsonify({'error': 'Photo not found'}), 404

    photo.is_deleted = True
    photo.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': f'Photo {photo_id} deleted'}), 200
