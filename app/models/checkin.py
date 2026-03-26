from app.config.db import db
from datetime import datetime
from sqlalchemy import Enum
class Check_in(db.Model):
    __tablename__ = "dailycheckin"

    checkin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    checkin_date = db.Column(db.Date, nullable=False)
    mood = db.Column(Enum('great', 'good', 'okay', 'bad', 'awful', name='mood_enum'))
    energy_level = db.Column(Enum('High', 'Medium', 'Low', 'Running on Empty', name='energy_enum'))
    hours_of_sleep = db.Column(db.Numeric(3, 1))
    soreness = db.Column(Enum('Very', 'Kind of', 'Barely', 'Not', name='soreness_enum'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='check_in')

    def __repr__(self):
        return f"<CheckIn(id={self.checkin_id}, user_id={self.user_id}>"