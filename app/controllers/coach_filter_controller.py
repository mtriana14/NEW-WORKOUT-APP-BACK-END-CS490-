from app.models.hire import Hire
from app.models.user import User
from app.models.coach import Coach
from app.config.db import db
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity

# get what coach the user is subbed to
def get_subscribed_coach():
    """
    Get the details of the coach the user is currently subscribed to
    ---
    tags:
      - Client Subscriptions
    security:
      - Bearer: []
    responses:
      200:
        description: Returns hire details and coach profile
        schema:
          type: object
          properties:
            hire:
              type: object
            coach:
              type: object
      404:
        description: Coach record not found
      500:
        description: Internal server error
    """
    try:
        user_id = get_jwt_identity()
        hire = Hire.query.filter_by(user_id=user_id, status='active').first()
        if not hire:
            return jsonify({"Note":"You are not currently subscribed to any coach"}), 200
        coach = Coach.query.filter_by(coach_id=hire.coach_id).first()
        if not coach:
            return jsonify({"Error":"Coach not found"}), 404
        return jsonify({
            "hire": hire.to_dict(),
            "coach": coach.to_dict()
        }), 200
    except Exception as e:
        print(e)
        return jsonify({"Failed":f"{e}"}), 500
    
def search_for_coaches():
    """
    Search for active/approved coaches by name or specialty
    ---
    tags:
      - Coach Discovery
    parameters:
      - in: query
        name: first_name
        type: string
        description: Search by coach's first name
      - in: query
        name: last_name
        type: string
        description: Search by coach's last name
      - in: query
        name: specialty
        type: string
        description: Search by coach's specialization
    responses:
      200:
        description: A list of coaches matching the search criteria
      400:
        description: Multiple query parameters provided or invalid parameters
      404:
        description: No coaches found matching criteria
    """
    try:
        first_name = request.args.get('first_name')
        last_name = request.args.get('last_name')
        specialty = request.args.get('specialty')
        param_count = sum([1 for param in [first_name, last_name, specialty] if param])
        
        if param_count > 1:
            return jsonify({"Failed":"Only one or none queires may be present"}), 400

        query = db.session.query(Coach, User).join(
            User, Coach.user_id == User.user_id
        ).filter(
            Coach.status.in_(['active', 'approved'])
        )

        if first_name:
            query = query.filter(User.first_name.ilike(f'%{first_name}%'))
        elif last_name:
            query = query.filter(User.first_name.ilike(f'%{last_name}%'))
        elif specialty:
            query = query.filter(Coach.specialization.ilike(f'%{specialty}%'))

        res = query.all()
        if not res:
            return jsonify({"Note":"No coaches found"}), 404
        
        coaches = []
        for coach, user in res:
            coaches.append({
                'coach_id': coach.coach_id,
                'name': f"{user.first_name} {user.last_name}",
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': user.phone,
                'profile_photo': user.profile_photo,
                'specialization': coach.specialization,
                'certifications': coach.certifications,
                'experience_years': coach.experience_years,
                'gym': coach.gym,
                'cost': float(coach.cost) if coach.cost else None,
                'hourly_rate': float(coach.hourly_rate) if coach.hourly_rate else None,
                'bio': coach.bio,
                'status': coach.status
            })

        return jsonify({"Coaches":coaches}), 200

    except Exception as e:
        print(e)
        return jsonify({"Failed":f"Invalid query parameters: {e}"}), 400