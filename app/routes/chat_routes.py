from flask import Blueprint
from app.controllers.chat_controller import get_or_create_convo, get_conversations, get_messages

chat_bp = Blueprint('chat', __name__)

chat_bp.route('/chat/conversations/<int:coach_id>', methods=['POST'])(get_or_create_convo)
chat_bp.route('/chat/conversations',                methods=['GET'])(get_conversations)
chat_bp.route('/chat/conversations/<int:conversation_id>/messages', methods=['GET'])(get_messages)