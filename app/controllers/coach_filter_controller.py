from app.models.hire import Hire
from app.models.user import User
from app.models.coach import Coach
from app.config.db import db
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity

# get what coach the user is subbed to
def get_subscribed_coach():
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
    
# STILL WORKING ON THIS DO NOT USE YET
def search_for_coaches():
    try:
        name = request.args.get('name', '').strip()
        specialty = request.args.get('specialty').strip()
        gym = request.args.get('gym')
        min_experience = request.args.get('min_experience')

        query = db.session.query(Coach, User).join(
            User, Coach.user_id == User.user_id
        ).filter(
            Coach.status.in_('active')
        )

        if name:
            search = f"%{name}%"
            query = query.filter(
                db.or_(
                    User.first_name.ilike(search),
                    User.last_name.ilike(search),
                    db.func.concat(User.first_name, ' ', User.last_name).ilike(search)
                )
            )

            if specialty:
                query = query.filter(Coach.specialization == specialty)

            if gym:
                query = query.filter(Coach.gym.ilike(f"%{gym}%"))
            
            if min_experience:
                query = query.filter(Coach.years_experience >= int(min_experience))

            res = query.order_by(User.first_name, User.last_name).all()

            if not res:
                return jsonify({"Note":"No coaches found",
                                "coaches":[]
                    }), 404
            coaches = []
            for coach, user in res:
                coaches.append({
                    'coach_id': coach.coach_id,
                    'name': f"{user.first_name} {user.last_name}",
                    'email': user.email,
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