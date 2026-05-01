from flask import Blueprint
from app.controllers.chat_controller import get_or_create_conversation, get_messages, send_message

chat_routes_bp = Blueprint('chat_routes', __name__)

chat_routes_bp.route('/chat/conversation', methods=['GET'])(get_or_create_conversation)
chat_routes_bp.route('/chat/<int:conversation_id>/messages', methods=['GET'])(get_messages)
chat_routes_bp.route('/chat/<int:conversation_id>/messages', methods=['POST'])(send_message)

from app.controllers.chat_controller import get_or_create_conversation, get_messages, send_message, get_coach_conversations

chat_routes_bp.route('/chat/coach/conversations', methods=['GET'])(get_coach_conversations)