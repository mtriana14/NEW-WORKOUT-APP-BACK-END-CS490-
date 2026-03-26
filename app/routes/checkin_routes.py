from flask import Blueprint
from app.controllers.survey_controller import create_checkin

checkin_bp = Blueprint('checkins',__name__)

checkin_bp.route('/checkins', methods=['POST'])(create_checkin)