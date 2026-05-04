from flask import request, jsonify
from app.config.db import db
from app.models.checkin import Check_in
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date

@jwt_required()
def create_checkin():
    """
    Submit a daily wellness check-in
    ---
    tags:
      - Check-ins
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - checkin_date
          properties:
            checkin_date:
              type: string
              example: "2026-04-30"
            mood:
              type: integer
              minimum: 1
              maximum: 10
            energy_level:
              type: integer
              minimum: 1
              maximum: 10
            hours_of_sleep:
              type: number
            soreness:
              type: integer
              minimum: 1
              maximum: 10
            notes:
              type: string
    responses:
      200:
        description: Check-in created
      400:
        description: Invalid date format
    """
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
        return jsonify({"Error":f"{e}"}), 500