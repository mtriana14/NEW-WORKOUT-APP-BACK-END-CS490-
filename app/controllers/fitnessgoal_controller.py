from flask import request, jsonify
from app.config.db import db
from app.models.fitnessgoals import FitnessGoal
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

VALID_STATUSES = {"active", "completed", "deleted"}


def parse_deadline(deadline_str):
    if not deadline_str:
        return None

    try:
        return datetime.strptime(deadline_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def validate_status(status):
    return status in VALID_STATUSES


@jwt_required()
def create_fitnessgoal():
    """
    Create a new fitness goal for the authenticated user
    ---
    tags:
      - Fitness Goals
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - goal_type
          properties:
            goal_type:
              type: string
              description: Description of the goal (e.g. "Lose weight")
            target_value:
              type: number
              description: Numeric target (e.g. 75)
            target_unit:
              type: string
              description: Unit of the target (e.g. "kg")
            deadline:
              type: string
              format: date
              description: Target completion date (YYYY-MM-DD)
            status:
              type: string
              enum: [active, completed, deleted]
              default: active
    responses:
      201:
        description: Fitness goal created successfully
      400:
        description: Missing or invalid fields
    """
    user_id = get_jwt_identity()
    data = request.json

    if not data:
        return jsonify({"Failed": "No request body provided"}), 400

    goal_type = data.get("goal_type")

    if not goal_type or not goal_type.strip():
        return jsonify({"Failed": "goal_type is required"}), 400

    # Validate status
    status = data.get("status", "active")

    if not validate_status(status):
        return jsonify({
            "Failed": f"Invalid status. Must be one of {list(VALID_STATUSES)}"
        }), 400

    # Validate target_value
    target_value = data.get("target_value")

    if target_value is not None:
        try:
            target_value = float(target_value)
        except (TypeError, ValueError):
            return jsonify({"Failed": "target_value must be numeric"}), 400

    # Parse deadline
    deadline_str = data.get("deadline")
    deadline = parse_deadline(deadline_str)

    if deadline_str and deadline is None:
        return jsonify({
            "Failed": "deadline must be in YYYY-MM-DD format"
        }), 400

    try:
        newgoal = FitnessGoal(
            user_id=user_id,
            goal_type=goal_type.strip(),
            target_value=target_value,
            target_unit=data.get("target_unit"),
            deadline=deadline,
            status=status
        )

        db.session.add(newgoal)
        db.session.commit()

        return jsonify(newgoal.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        print(e)

        return jsonify({
            "Failed": f"Some error occurred: {str(e)}"
        }), 500


@jwt_required()
def delete_fitnessgoal(goal_id):
    """
    Soft delete a fitness goal
    ---
    tags:
      - Fitness Goals
    security:
      - Bearer: []
    parameters:
      - in: path
        name: goal_id
        type: integer
        required: true
    responses:
      200:
        description: Fitness goal deleted
      404:
        description: Goal not found
      500:
        description: Server error
    """

    user_id = get_jwt_identity()

    goal = FitnessGoal.query.filter_by(
        goal_id=goal_id,
        user_id=user_id
    ).first()

    if not goal:
        return jsonify({"Failed": "Invalid goal id"}), 404

    try:
        # Soft delete
        goal.status = "deleted"
        goal.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            "Success": f"Goal {goal_id} has been deleted"
        }), 200

    except Exception as e:
        db.session.rollback()
        print(e)

        return jsonify({
            "Failed": "Some error has occurred"
        }), 500


@jwt_required()
def get_fitnessgoal(goal_id):
    """
    Get a specific fitness goal by ID
    ---
    tags:
      - Fitness Goals
    security:
      - Bearer: []
    parameters:
      - in: path
        name: goal_id
        type: integer
        required: true
    responses:
      200:
        description: Fitness goal details retrieved
      404:
        description: Goal not found
    """

    user_id = get_jwt_identity()

    goal = FitnessGoal.query.filter(
        FitnessGoal.goal_id == goal_id,
        FitnessGoal.user_id == user_id,
        FitnessGoal.status != "deleted"
    ).first()

    if not goal:
        return jsonify({"Failed": "Goal not found"}), 404

    return jsonify(goal.to_dict()), 200


@jwt_required()
def get_all_fitnessgoals():
    """
    Get all fitness goals for the current user
    ---
    tags:
      - Fitness Goals
    security:
      - Bearer: []
    responses:
      200:
        description: A list of fitness goals
      500:
        description: Server error
    """

    try:
        user_id = get_jwt_identity()

        goals = (
            FitnessGoal.query
            .filter(
                FitnessGoal.user_id == user_id,
                FitnessGoal.status != "deleted"
            )
            .order_by(FitnessGoal.created_at.desc())
            .all()
        )

        if not goals:
            return jsonify({"Failed": "No fitness goals found"}), 404

        return jsonify({
            "Goals": [goal.to_dict() for goal in goals]
        }), 200

    except Exception as e:
        print(e)

        return jsonify({
            "Failed": f"{e}"
        }), 500


@jwt_required()
def edit_fitnessgoal(goal_id):
    """
    Update a fitness goal
    ---
    tags:
      - Fitness Goals
    security:
      - Bearer: []
    parameters:
      - in: path
        name: goal_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            goal_type:
              type: string
            target_value:
              type: number
            target_unit:
              type: string
            deadline:
              type: string
            status:
              type: string
              enum: [active, completed, deleted]
    responses:
      200:
        description: Fitness goal updated
      404:
        description: Goal not found
      500:
        description: Server error
    """

    user_id = get_jwt_identity()
    data = request.json

    if not data:
        return jsonify({"Failed": "No body present"}), 400

    goal = FitnessGoal.query.filter_by(
        goal_id=goal_id,
        user_id=user_id
    ).first()

    if not goal:
        return jsonify({"Error": "Goal not found"}), 404

    try:
        # goal_type
        if "goal_type" in data:
            if not data["goal_type"].strip():
                return jsonify({
                    "Failed": "goal_type cannot be empty"
                }), 400

            goal.goal_type = data["goal_type"].strip()

        # target_value
        if "target_value" in data:
            if data["target_value"] is None or data["target_value"] == "":
                goal.target_value = None
            else:
                try:
                    goal.target_value = float(data["target_value"])
                except (TypeError, ValueError):
                    return jsonify({
                        "Failed": "target_value must be numeric"
                    }), 400

        # target_unit
        if "target_unit" in data:
            goal.target_unit = data["target_unit"]

        # deadline
        if "deadline" in data:
            if not data["deadline"]:
                goal.deadline = None
            else:
                parsed_deadline = parse_deadline(data["deadline"])

                if parsed_deadline is None:
                    return jsonify({
                        "Failed": "deadline must be in YYYY-MM-DD format"
                    }), 400

                goal.deadline = parsed_deadline

        # status
        if "status" in data:
            if not validate_status(data["status"]):
                return jsonify({
                    "Failed": f"Invalid status. Must be one of {list(VALID_STATUSES)}"
                }), 400

            goal.status = data["status"]

        goal.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            "Success": "Fitness goal updated",
            "Goal": goal.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        print(e)

        return jsonify({
            "Failed": f"Some error occurred: {str(e)}"
        }), 500