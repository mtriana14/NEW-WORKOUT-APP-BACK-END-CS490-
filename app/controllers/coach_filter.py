from flask import jsonify, request
from app.config.db import db
from app.models.coach import Coach
from app.models.subscription import Subscription
from app.models.user import User
from flask_jwt_extended import get_jwt_identity, jwt_required

# get all the subscriptions that a user has
@jwt_required()
def get_all_coaches():
    user_id = get_jwt_identity()
    coach_id = request.args.get('coach_id', type=int)
    coach_name = request.args.get('name')
    query = db.session.query(Coach, User, Subscription).join(
    Subscription, Coach.coach_id == Subscription.coach_id
    ).join(
        User, Coach.user_id == User.user_id
    ).filter(
        Subscription.user_id == user_id,
        Subscription.status == 'active'
    )

    if coach_id:
        search = f"%{coach_name}%"
        query = query.filter(
            db.or_(
                User.first_name.ilike(search),
                User.last_name.ilike(search),
                db.func.concat(User.first_name, ' ', User.last_name).ilike(search)
            )
        )

        res = query.all()

        if not res:
            return jsonify({"Error":"No subscriptiosn found"}), 404
        
        coaches = []
        