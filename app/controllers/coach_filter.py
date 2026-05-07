from flask import jsonify, request
from app.config.db import db
from app.models.coach import Coach
from app.models.subscription import Subscription
from app.models.user import User
from flask_jwt_extended import get_jwt_identity, jwt_required

@jwt_required()
def get_all_coaches():
    """
    Get all coaches the authenticated user is subscribed to
    ---
    tags:
      - Coaches
    security:
      - Bearer: []
    parameters:
      - in: query
        name: coach_id
        type: integer
        required: false
        description: Filter by coach ID
      - in: query
        name: name
        type: string
        required: false
        description: Search by coach name
    responses:
      200:
        description: List of subscribed coaches
        schema:
          type: object
          properties:
            coaches:
              type: array
              items:
                type: object
      404:
        description: No subscriptions found
    """
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
        