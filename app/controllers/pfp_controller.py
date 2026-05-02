import os
from app.config.db import db
from app.models.user import User
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import jsonify, request, current_app
from flask_jwt_extended import get_jwt_identity

extensions = {'png','jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.',1)[1].lower() in extensions

def upload_pfp():
    """
    Upload a profile photo
    ---
    tags:
      - User Management
    security:
      - Bearer: []
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: profile_photo
        type: file
        required: true
        description: Image file (png, jpg, jpeg, gif, webp)
    responses:
      200:
        description: Profile photo uploaded successfully
      400:
        description: No file provided or invalid file type
      500:
        description: Server error
    """
    try:
        user_id = get_jwt_identity()
        if 'profile_photo' not in request.files:
            return jsonify({"Failed":"No file in the request"}), 400
        
        file = request.files['profile_photo']

        if file.filename == '':
            return jsonify({"Failed":"No profile pciture selected"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"user_{user_id}_{timestamp}_{filename}"
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads/profile_photos')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            db_path = f"/static/uploads/profile_photos/{unique_filename}"
            user = User.query.get(user_id)
            user.profile_photo = db_path
            db.session.commit()
            return jsonify({"Success":"Profile photo uploaded"}), 200
        else:
            return jsonify({"Failed":"Not a vlaid filename"}), 400

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"Failed":f"{e}"}), 500