from app.config.db import db
from datetime import datetime

class MessageList(db.Model):
    __tablename__ = 'messagelist'
    MessageList_id  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    coach_id        = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    last_message_at = db.Column(db.DateTime, nullable=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    messages = db.relationship('Message', backref='messagelist', lazy=True)

    def to_dict(self):
        return {
            'MessageList_id':  self.MessageList_id,
            'user_id':         self.user_id,
            'coach_id':        self.coach_id,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None,
            'created_at':      self.created_at.isoformat()
        }