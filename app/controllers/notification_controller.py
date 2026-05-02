from flask import request, jsonify
from app.config.db import db
from app.models.notification import Notification
from app.models.user import User


def get_all_notifications():
    """
    Get all notifications (admin)
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    responses:
      200:
        description: List of all notifications across all users
    """
    notifications = Notification.query.order_by(
        Notification.created_at.desc()
    ).all()

    user_ids = {n.user_id for n in notifications}
    users = {
        u.user_id: f'{u.first_name} {u.last_name}'
        for u in User.query.filter(User.user_id.in_(user_ids)).all()
    }

    result = [
        {
            'id':             n.notification_id,
            'notification_id': n.notification_id,
            'user_id':        n.user_id,
            'user_name':      users.get(n.user_id, 'Unknown'),
            'title':          n.title,
            'message':        n.message,
            'type':           n.type,
            'is_read':        n.is_read,
            'created_at':     str(n.created_at)
        }
        for n in notifications
    ]

    return jsonify({'notifications': result}), 200


def get_user_notifications(user_id):
    """
    Get notifications for a specific user
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
    responses:
      200:
        description: List of notifications for the user
    """
    notifications = Notification.query.filter_by(
        user_id=user_id
    ).order_by(Notification.created_at.desc()).all()

    result = [
        {
            'id':    n.notification_id,
            'title': n.title,
            'message': n.message,
            'type':  n.type,
            'is_read': n.is_read,
            'created_at': str(n.created_at)
        }
        for n in notifications
    ]
    return jsonify({'notifications': result}), 200


def get_unread_notifications(user_id):
    """
    Get unread notifications for a user
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
    responses:
      200:
        description: Unread notifications with count
    """
    notifications = Notification.query.filter_by(
        user_id=user_id, is_read=False
    ).order_by(Notification.created_at.desc()).all()

    result = [
        {
            'id':    n.notification_id,
            'title': n.title,
            'message': n.message,
            'type':  n.type,
            'created_at': str(n.created_at)
        }
        for n in notifications
    ]
    return jsonify({
        'notifications': result,
        'unread_count': len(result)
    }), 200


def mark_as_read(notification_id):
    """
    Mark a notification as read
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    parameters:
      - in: path
        name: notification_id
        type: integer
        required: true
    responses:
      200:
        description: Notification marked as read
      404:
        description: Notification not found
    """
    notification = Notification.query.filter_by(
        notification_id=notification_id
    ).first()
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404

    notification.is_read = True
    db.session.commit()
    return jsonify({'message': 'Notification marked as read'}), 200


def mark_all_as_read(user_id):
    """
    Mark all notifications as read for a user
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
    responses:
      200:
        description: All notifications marked as read
    """
    Notification.query.filter_by(
        user_id=user_id, is_read=False
    ).update({'is_read': True})
    db.session.commit()
    return jsonify({'message': 'All notifications marked as read'}), 200


def send_notification():
    """
    Send a notification to a user
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - user_id
            - title
            - message
          properties:
            user_id:
              type: integer
            title:
              type: string
            message:
              type: string
            type:
              type: string
              default: system
    responses:
      201:
        description: Notification sent
      400:
        description: Missing required fields
    """
    data = request.get_json()
    if not data.get('user_id') or not data.get('title') or not data.get('message'):
        return jsonify({'error': 'user_id, title and message are required'}), 400

    notification = Notification(
        user_id=data.get('user_id'),
        title=data.get('title'),
        message=data.get('message'),
        type=data.get('type', 'system')
    )
    db.session.add(notification)
    db.session.commit()
    return jsonify({
        'message': 'Notification sent successfully',
        'id': notification.notification_id
    }), 201


def delete_notification(notification_id):
    """
    Delete a notification
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    parameters:
      - in: path
        name: notification_id
        type: integer
        required: true
    responses:
      200:
        description: Notification deleted
      404:
        description: Notification not found
    """
    notification = Notification.query.filter_by(
        notification_id=notification_id
    ).first()
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404

    db.session.delete(notification)
    db.session.commit()
    return jsonify({'message': 'Notification deleted successfully'}), 200