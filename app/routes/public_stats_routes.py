from flask import Blueprint
from app.controllers.public_stats_controller import get_public_stats, get_public_exercises

public_stats_bp = Blueprint("public_stats", __name__)

public_stats_bp.route("/public/stats",     methods=["GET"])(get_public_stats)
public_stats_bp.route("/public/exercises", methods=["GET"])(get_public_exercises)
