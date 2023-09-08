from backend import db
from sqlalchemy import Enum

class ActionType(db.Model):
    """Model representing action types."""
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False, unique=True)
    
    actions = db.relationship('Action', back_populates='action_type', lazy=True)
    bills = db.relationship('Bill', back_populates='action_type')

    def __repr__(self):
        return f'<ActionType {self.description}>'