from backend import db
from sqlalchemy import Enum

action_actioncode = db.Table('action_actioncode',
        db.Column('action_id', db.Integer, db.ForeignKey('action.id'), primary_key=True),
        db.Column('action_code_id', db.Integer, db.ForeignKey('action_code.id'), primary_key=True)
    )

class Action(db.Model):
    """Model representing actions."""
    id = db.Column(db.Integer, primary_key=True)
    action_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    chamber = db.Column(Enum('House', 'Senate', name='chamber_types'), nullable=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    action_type_id = db.Column(db.Integer, db.ForeignKey('action_type.id'), nullable=True, index=True)
    is_latest = db.Column(db.Boolean, default=False)
    
    action_type = db.relationship('ActionType', back_populates='actions', lazy=True)
    action_codes = db.relationship('ActionCode', secondary=action_actioncode, 
    back_populates='action_code_relations')
    bill = db.relationship('Bill', back_populates='actions')

    def __repr__(self):
        return f'<Action {self.id} on {self.action_date}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "action_date": self.action_date,
            "description": self.description,
            "chamber": self.chamber,
            "bill_id": self.bill_id,
            "action_type_id": self.action_type_id,
            "is_latest": self.is_latest,
            "action_type": self.action_type.to_dict() if self.action_type else None,
            "bill": self.bill.to_dict() if self.bill else None,
            "action_codes": [action_code.to_dict() for action_code in self.action_codes],
        }

class ActionCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    action_code_relations = db.relationship('Action', secondary=action_actioncode, back_populates='action_codes')

    def __repr__(self):
        return f'<ActionCode {self.code}: {self.description}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "description": self.description,
            "actions": [action.to_dict() for action in self.actions],
        }