from backend import db

class ActionType(db.Model):
    """Model representing action types."""
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False, unique=True)
    is_latest = db.Column(db.Boolean, default=False)
    action_type = db.Column(db.String(200), nullable=False)
    
    actions = db.relationship('Action', back_populates='action_type', lazy=True)
    bills = db.relationship('Bill', back_populates='action_type')

    def __repr__(self):
        return f'<ActionType {self.description}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "is_latest": self.is_latest,
            "action_type": self.action_type,
            "actions": [action.to_dict() for action in self.actions],
            "bills": [bill.to_dict() for bill in self.bills],
        }