from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.config.db import db
from app.models.message import Message
from app.models.message_list import MessageList
from datetime import datetime

chat_bp = Blueprint('chat', __name__)


# GET /api/chat/conversation  — obtener o crear conversación entre user y coach
@chat_bp.route('/api/chat/conversation', methods=['GET'])
@jwt_required()
def get_or_create_conversation():
    current_user_id = int(get_jwt_identity())
    coach_id = request.args.get('coach_id', type=int)

    if not coach_id:
        return jsonify({'error': 'coach_id is required'}), 400

    convo = MessageList.query.filter_by(
        user_id=current_user_id, coach_id=coach_id
    ).first()

    if not convo:
        convo = MessageList(user_id=current_user_id, coach_id=coach_id)
        db.session.add(convo)
        db.session.commit()

    return jsonify(convo.to_dict()), 200


# GET /api/chat/<conversation_id>/messages  — historial
@chat_bp.route('/api/chat/<int:conversation_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(conversation_id):
    current_user_id = int(get_jwt_identity())

    convo = MessageList.query.get(conversation_id)
    if not convo:
        return jsonify({'error': 'Conversation not found'}), 404

    # Verificar que el usuario pertenece a esta conversación
    if convo.user_id != current_user_id and convo.coach_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    messages = Message.query.filter_by(
        conversation_id=conversation_id
    ).order_by(Message.created_at.asc()).all()

    # Marcar como leídos
    for m in messages:
        if m.sender_id != current_user_id:
            m.is_read = True
    db.session.commit()

    return jsonify([m.to_dict() for m in messages]), 200


# POST /api/chat/<conversation_id>/messages  — enviar mensaje
@chat_bp.route('/api/chat/<int:conversation_id>/messages', methods=['POST'])
@jwt_required()
def send_message(conversation_id):
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    content = data.get('content', '').strip()

    if not content:
        return jsonify({'error': 'content is required'}), 400

    convo = MessageList.query.get(conversation_id)
    if not convo:
        return jsonify({'error': 'Conversation not found'}), 404

    if convo.user_id != current_user_id and convo.coach_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    msg = Message(
        conversation_id=conversation_id,
        sender_id=current_user_id,
        content=content
    )
    db.session.add(msg)

    convo.last_message_at = datetime.utcnow()
    db.session.commit()

    return jsonify(msg.to_dict()), 201

# GET /api/chat/coach/conversations — lista de conversaciones del coach
@chat_bp.route('/chat/coach/conversations', methods=['GET'])
@jwt_required()
def get_coach_conversations():
    current_user_id = int(get_jwt_identity())

    convos = MessageList.query.filter_by(coach_id=current_user_id).order_by(
        MessageList.last_message_at.desc()
    ).all()

    result = []
    for c in convos:
        last_msg = Message.query.filter_by(
            conversation_id=c.MessageList_id
        ).order_by(Message.created_at.desc()).first()

        unread = Message.query.filter_by(
            conversation_id=c.MessageList_id,
            is_read=False
        ).filter(Message.sender_id != current_user_id).count()

        result.append({
            'conversation_id': c.MessageList_id,
            'user_id':         c.user_id,
            'last_message':    last_msg.content if last_msg else "",
            'last_time':       last_msg.created_at.isoformat() if last_msg else None,
            'unread_count':    unread
        })

    return jsonify(result), 200