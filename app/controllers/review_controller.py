from flask import request, jsonify
from app.config.db import db
from app.models.review import Review
from app.models.hire import Hire
from app.models.coach import Coach
from flask_jwt_extended import get_jwt_identity
from datetime import datetime


def leave_review(coach_id):
    """
    Submit or update a review for a coach
    ---
    tags:
      - Reviews
    security:
      - Bearer: []
    parameters:
      - in: path
        name: coach_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - rating
          properties:
            rating:
              type: integer
              minimum: 1
              maximum: 5
            comment:
              type: string
    responses:
      200:
        description: Review updated
      201:
        description: Review submitted
      400:
        description: Missing or invalid rating
      403:
        description: You have not worked with this coach
    """
    user_id = int(get_jwt_identity())

    hire = Hire.query.filter_by(user_id=user_id, coach_id=coach_id).first()
    if not hire:
        return jsonify({'error': 'You can only review a coach you have worked with'}), 403

    data = request.get_json()
    rating = data.get('rating')

    if rating is None:
        return jsonify({'error': 'rating is required'}), 400
    if not isinstance(rating, int) or not (1 <= rating <= 5):
        return jsonify({'error': 'rating must be an integer between 1 and 5'}), 400

    comment = data.get('comment', '')

    existing = Review.query.filter_by(user_id=user_id, coach_id=coach_id).first()
    if existing:
        existing.rating = rating
        existing.comment = comment
        existing.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({
            'message': 'Review updated successfully',
            'review':  existing.to_dict()
        }), 200

    review = Review(
        user_id=user_id,
        coach_id=coach_id,
        rating=rating,
        comment=comment
    )
    db.session.add(review)
    db.session.commit()

    return jsonify({
        'message': 'Review submitted successfully',
        'review':  review.to_dict()
    }), 201


def get_coach_reviews(coach_id):
    """
    Get all reviews for a coach
    ---
    tags:
      - Reviews
    parameters:
      - in: path
        name: coach_id
        type: integer
        required: true
    responses:
      200:
        description: List of reviews with average rating
      404:
        description: Coach not found
    """
    coach = Coach.query.get(coach_id)
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404

    reviews = Review.query.filter_by(coach_id=coach_id).order_by(Review.created_at.desc()).all()

    avg_rating = None
    if reviews:
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 2)

    return jsonify({
        'coach_id':   coach_id,
        'avg_rating': avg_rating,
        'total':      len(reviews),
        'reviews':    [r.to_dict() for r in reviews]
    }), 200


def delete_review(coach_id):
    """
    Delete your review for a coach
    ---
    tags:
      - Reviews
    security:
      - Bearer: []
    parameters:
      - in: path
        name: coach_id
        type: integer
        required: true
    responses:
      200:
        description: Review deleted
      404:
        description: Review not found
    """
    user_id = int(get_jwt_identity())

    review = Review.query.filter_by(user_id=user_id, coach_id=coach_id).first()
    if not review:
        return jsonify({'error': 'Review not found'}), 404

    db.session.delete(review)
    db.session.commit()
    return jsonify({'message': 'Review deleted successfully'}), 200