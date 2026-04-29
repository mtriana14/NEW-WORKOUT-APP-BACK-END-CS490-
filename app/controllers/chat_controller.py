from flask import jsonify, request, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_socketio import join_room, emit
from app.config.db import db
from app.models.message import Message
from app.models.messagelist import MessageList
from app.models.coach import Coach
from app.models.user import User
from app import socketio
from datetime import datetime 
import json

@jwt_required()
def get_or_create_convo(coach_id):
    try:
        user_id = get_jwt_identity()
        coach = Coach.query.filter_by(user_id = coach_id).first()
        if not coach:
            return jsonify({"Failed":"Can only start convos with coaches"}), 400
        
        if int(user_id) == int(coach_id):
            return jsonify({"Failed":"Cant start convo with yourself"}), 400
        
        convo = MessageList.query.filter_by(user_id=user_id, coach_id=coach_id).first()
        if not convo:
            convo = MessageList(user_id=user_id, coach_id=coach_id)
            db.session.add(convo)
            db.session.commit()
        
        return jsonify({"Conversation":convo.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"Failed":str(e)}), 500

@jwt_required()
def get_conversations():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({"Failed":"User not found"}), 404
        if user.role == 'coach':
            convos = MessageList.query.filter_by(coach_id=user_id).all()
        else:
            convos = MessageList.query.filter_by(user_id=user_id).all()
        return jsonify({"Conversations":[convo.to_dict() for convo in convos]}), 200
    except Exception as e:
        print(e)
        return jsonify({"Failed":str(e)}), 500

@jwt_required()
def get_messages(conversation_id):
    try:
        user_id = get_jwt_identity()
        convo = MessageList.query.filter(
            (MessageList.MessageList_id == conversation_id) &
            ((MessageList.user_id == user_id) | (MessageList.coach_id == user_id))
        ).first()
        if not convo:
            return jsonify({"Failed":"No convo found"}), 404
        messages = Message.query.filter_by(conversation_id=conversation_id).all()
        if not messages:
            return jsonify({"Failed":"No messages found"}), 404
        
        Message.query.filter_by(conversation_id=conversation_id, is_read=False) \
        .filter(Message.sender_id != user_id) \
        .update({"is_read": True})
        db.session.commit()
        return jsonify({"messages": [m.to_dict() for m in messages]}), 200
        
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"Failed":str(e)}), 500
    
@socketio.on('join')
def handle_join(data):
    try:
        if isinstance(data, str):
            data = json.loads(data)
        room = str(data['conversation_id'])
        join_room(room)
        emit('status', {'message':f'joined conversation {room}'}, to=room)
    except Exception as e:
        emit('error', {'message':str(e)})

@socketio.on('send_message')
def handle_message(data):
    try:
        if isinstance(data, str):
            data = json.loads(data)

        conversation_id = int(data['conversation_id'])
        sender_id       = int(data['sender_id'])
        content         = data['content']

        if not content or not content.strip():
            emit('error', {'message': 'Message content cannot be empty'})
            return

        conversation = MessageList.query.filter(
            (MessageList.MessageList_id == conversation_id) &
            ((MessageList.user_id == sender_id) | (MessageList.coach_id == sender_id))
        ).first()

        if not conversation:
            emit('error', {'message': 'Conversation not found or not authorized'})
            return

        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content
        )
        db.session.add(message)

        conversation.last_message_at = datetime.utcnow()
        db.session.commit()

        emit('new_message', message.to_dict(), to=str(conversation_id))

    except Exception as e:
        db.session.rollback()
        emit('error', {'message': str(e)})

@socketio.on('mark_read')
def handle_mark_read(data):
    try:
        if isinstance(data, str):
            data = json.loads(data)

        conversation_id = int(data['conversation_id'])
        user_id         = int(data['user_id'])

        with current_app.app_context():
            unread_messages = Message.query.filter(
                Message.conversation_id == conversation_id,
                Message.is_read == False,
                Message.sender_id != user_id
            ).all()

            if not unread_messages:
                emit('messages_read', {'conversation_id': conversation_id, 'count': 0})
                return

            for message in unread_messages:
                message.is_read = True

            db.session.commit()

        emit('messages_read', {
            'conversation_id': conversation_id,
            'count': len(unread_messages)  
        })
        emit('messages_read', {
            'conversation_id': conversation_id,
            'count': len(unread_messages)
        }, to=str(conversation_id))

    except Exception as e:
        db.session.rollback()
        print(f"mark_read error: {e}")
        emit('error', {'message': str(e)})

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')