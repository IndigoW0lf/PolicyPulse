from backend import db

class ActionType(db.Model):
    """Model representing action types."""
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False, unique=True)
    action_type = db.Column(db.String, nullable=False)
    
    actions = db.relationship('Action', back_populates='action_type', lazy=True)
    bills = db.relationship('Bill', back_populates='action_type')

    def __repr__(self):
        return f'<ActionType {self.description}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "action_type": self.action_type,
            "actions": [action.to_dict() for action in self.actions],
            "bills": [bill.to_dict() for bill in self.bills],
        }