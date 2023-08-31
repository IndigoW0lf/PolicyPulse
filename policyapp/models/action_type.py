from policyapp import db

class ActionType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    actions = db.relationship('Action', backref='action_type', lazy=True)