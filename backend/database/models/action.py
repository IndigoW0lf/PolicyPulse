from backend import db
from sqlalchemy import Enum

class Action(db.Model):
    """Model representing actions."""
    id = db.Column(db.Integer, primary_key=True)
    action_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    chamber = db.Column(Enum('House', 'Senate', name='chamber_types'), nullable=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    action_type_id = db.Column(db.Integer, db.ForeignKey('action_type.id'), nullable=True, index=True)
    
    action_type = db.relationship('ActionType', back_populates='actions', lazy=True)
    bill = db.relationship('Bill', back_populates='actions', lazy=True)

    def __repr__(self):
        return f'<Action {self.id} on {self.action_date}>'
