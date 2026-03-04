from flask import request, jsonify
from app.config.db import db
from app.models.notification import Notification

def get_user_notifications(user_id):
    """Get all notifications for a user."""
    notifications = Notification.query.filter_by(
        user_id=user_id
    ).order_by(Notification.created_at.desc()).all()

    result = [
        {
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'type': n.type,
            'is_read': n.is_read,
            'created_at': str(n.created_at)
        }
        for n in notifications
    ]

    return jsonify({'notifications': result}), 200


def get_unread_notifications(user_id):
    """Get all unread notifications for a user."""
    notifications = Notification.query.filter_by(
        user_id=user_id, is_read=False
    ).order_by(Notification.created_at.desc()).all()

    result = [
        {
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'type': n.type,
            'created_at': str(n.created_at)
        }
        for n in notifications
    ]

    return jsonify({
        'notifications': result,
        'unread_count': len(result)
    }), 200


def mark_as_read(notification_id):
    """Mark a single notification as read."""
    notification = Notification.query.filter_by(id=notification_id).first()
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404

    notification.is_read = True
    db.session.commit()
    return jsonify({'message': 'Notification marked as read'}), 200


def mark_all_as_read(user_id):
    """Mark all notifications as read for a user."""
    Notification.query.filter_by(
        user_id=user_id, is_read=False
    ).update({'is_read': True})

    db.session.commit()
    return jsonify({'message': 'All notifications marked as read'}), 200


def send_notification():
    """Send a notification to a user (used internally by other controllers)."""
    data = request.get_json()

    # Validate required fields
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
    return jsonify({'message': 'Notification sent successfully', 'id': notification.id}), 201


def delete_notification(notification_id):
    """Delete a notification."""
    notification = Notification.query.filter_by(id=notification_id).first()
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404

    db.session.delete(notification)
    db.session.commit()
    return jsonify({'message': 'Notification deleted successfully'}), 200