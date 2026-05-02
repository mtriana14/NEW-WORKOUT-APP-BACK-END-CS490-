from app.config.db import db
from datetime import datetime


class ProgressPhoto(db.Model):
    """Before / progress / after photos a user uploads to track their transformation."""
    __tablename__ = 'progressphotos'

    photo_id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)

    file_path  = db.Column(db.String(500), nullable=False)
    label      = db.Column(db.Enum('before', 'progress', 'after'), nullable=False, default='progress')
    caption    = db.Column(db.Text, nullable=True)
    weight_at_time = db.Column(db.Numeric(5, 2), nullable=True)
    taken_on   = db.Column(db.Date, nullable=True)

    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='progress_photos')

    def to_dict(self):
        return {
            'photo_id':       self.photo_id,
            'user_id':        self.user_id,
            'file_path':      self.file_path,
            'label':          self.label,
            'caption':        self.caption,
            'weight_at_time': float(self.weight_at_time) if self.weight_at_time else None,
            'taken_on':       self.taken_on.isoformat() if self.taken_on else None,
            'created_at':     self.created_at.isoformat() if self.created_at else None,
        }
