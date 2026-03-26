from app.config.db import db
from datetime import datetime
from sqlalchemy import Enum

class FitnessGoal(db.Model):
    __tablename__ = 'fitnessgoals'
    
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    goal_type = db.Column(db.String(100), nullable=False)
    target_value = db.Column(db.Numeric(10, 2))
    target_unit = db.Column(db.String(20))
    deadline = db.Column(db.Date)
    status = db.Column(
        Enum('active', 'completed', 'deleted', name='goal_status_enum'),
        nullable=False,
        default='active'
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to User model
    user = db.relationship('User', backref='fitness_goals')
    
    def __repr__(self):
        return f"<FitnessGoal(id={self.goal_id}, user_id={self.user_id}, type={self.goal_type}, status={self.status})>"
    
    def to_dict(self):
        return {
            'goal_id': self.goal_id,
            'user_id': self.user_id,
            'goal_type': self.goal_type,
            'target_value': float(self.target_value) if self.target_value else None,
            'target_unit': self.target_unit,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
