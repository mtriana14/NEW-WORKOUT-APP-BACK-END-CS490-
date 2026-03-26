from flask import request, jsonify
from app.config.db import db
from app.models.checkin import Check_in
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date

@jwt_required()
def create_checkin():
    try:
        user_id = get_jwt_identity()
        data = request.json
        try:
            checkin_date = datetime.strptime(data.get('checkin_date'), '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"Error":"Invalid date"}), 400
        
        checkin = Check_in(
            user_id=user_id,
            checkin_date=checkin_date,
            mood=data.get('mood'),
            energy_level=data.get('energy_level'),
            hours_of_sleep=data.get('hours_of_sleep'),
            soreness=data.get('soreness'),
            notes=data.get('notes')
        )

        db.session.add(checkin)
        db.session.commit()
        return jsonify({"Success":"Checkin created"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"Error":f"{e}"})