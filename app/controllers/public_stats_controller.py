from flask import jsonify
from app.config.db import db
from app.models.user import User
from app.models.coach import Coach
from app.models.review import Review
from app.models.exercise import Exercise
from sqlalchemy import func


def get_public_stats():
    """
    Get public platform statistics and top-rated coaches
    ---
    tags:
      - Public
    responses:
      200:
        description: Platform stats and top 3 coaches by average rating
        schema:
          type: object
          properties:
            total_members:
              type: integer
              description: Total registered users
            active_coaches:
              type: integer
              description: Coaches with active or approved status
            total_reviews:
              type: integer
              description: Total reviews submitted platform-wide
            top_coaches:
              type: array
              items:
                type: object
                properties:
                  coach_name:
                    type: string
                  avg_rating:
                    type: number
                    format: float
                  review_count:
                    type: integer
                  top_comment:
                    type: string
                    nullable: true
                  reviewer_name:
                    type: string
                    nullable: true
    """
    total_members = db.session.query(func.count(User.user_id)).scalar() or 0

    active_coaches = (
        db.session.query(func.count(Coach.coach_id))
        .filter(Coach.status.in_(["active", "approved"]))
        .scalar() or 0
    )

    total_reviews = db.session.query(func.count(Review.review_id)).scalar() or 0

    # Top 3 coaches ranked by avg rating, then review count
    coach_stats = (
        db.session.query(
            Coach.coach_id,
            Coach.user_id,
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.review_id).label("review_count"),
        )
        .join(Review, Review.coach_id == Coach.coach_id)
        .group_by(Coach.coach_id, Coach.user_id)
        .order_by(func.avg(Review.rating).desc(), func.count(Review.review_id).desc())
        .limit(3)
        .all()
    )

    top_coaches = []
    for coach_id, user_id, avg_rating, review_count in coach_stats:
        user = User.query.filter_by(user_id=user_id).first()
        recent = (
            Review.query
            .filter(
                Review.coach_id == coach_id,
                Review.comment != None,
                Review.comment != "",
            )
            .order_by(Review.created_at.desc())
            .first()
        )
        reviewer_name = None
        if recent and recent.client:
            reviewer_name = f"{recent.client.first_name} {recent.client.last_name}".strip()

        top_coaches.append({
            "coach_name":    f"{user.first_name} {user.last_name}".strip() if user else "Unknown",
            "avg_rating":    round(float(avg_rating), 1),
            "review_count":  int(review_count),
            "top_comment":   recent.comment if recent else None,
            "reviewer_name": reviewer_name,
        })

    return jsonify({
        "total_members":  int(total_members),
        "active_coaches": int(active_coaches),
        "total_reviews":  int(total_reviews),
        "top_coaches":    top_coaches,
    }), 200


def get_public_exercises():
    """
    Get all active exercises (public, no auth required)
    ---
    tags:
      - Public
    responses:
      200:
        description: List of active exercises
        schema:
          type: object
          properties:
            exercises:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  muscle_group:
                    type: string
                  equipment_type:
                    type: string
                  difficulty:
                    type: string
    """
    exercises = Exercise.query.filter_by(is_active=True).order_by(Exercise.name).all()
    return jsonify({
        "exercises": [
            {
                "id":             ex.e_id,
                "name":           ex.name,
                "muscle_group":   ex.muscle_group,
                "equipment_type": ex.equipment_type,
                "difficulty":     ex.difficulty,
            }
            for ex in exercises
        ]
    }), 200
