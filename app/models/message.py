from app.config.db import db
from datetime import datetime

class Message(db.Model):
    __tablename__ = 'messages'

    message_id      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('messagelist.MessageList_id'), nullable=False)
    sender_id       = db.Column(db.Integer, nullable=False)
    content         = db.Column(db.Text, nullable=False)
    is_read         = db.Column(db.Boolean, default=False)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'message_id':      self.message_id,
            'conversation_id': self.conversation_id,
            'sender_id':       self.sender_id,
            'content':         self.content,
            'is_read':         self.is_read,
            'created_at':      self.created_at.isoformat() if self.created_at else None,
        }