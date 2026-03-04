from app.config.db import db
from datetime import datetime

class Notification(db.Model):
    """Notification model - stores push notifications for all users."""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.Enum(
        'coach_request', 'request_accepted', 'request_declined',
        'new_workout', 'new_meal_plan', 'payment', 'system'
    ), nullable=False, default='system')
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='notifications')

    def __repr__(self):
        return f'<Notification {self.user_id} - {self.type}>'