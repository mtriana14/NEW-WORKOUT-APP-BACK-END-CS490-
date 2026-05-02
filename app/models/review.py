from app.config.db import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = 'reviews'

    review_id  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    coach_id   = db.Column(db.Integer, db.ForeignKey('Coaches.coach_id'), nullable=False)
    rating     = db.Column(db.Integer, nullable=False)
    comment    = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'coach_id', name='unique_review'),
    )

    client = db.relationship('User', backref='reviews')
    coach  = db.relationship('Coach', backref='reviews')

    def to_dict(self):
        return {
            'review_id':  self.review_id,
            'user_id':    self.user_id,
            'coach_id':   self.coach_id,
            'rating':     self.rating,
            'comment':    self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }