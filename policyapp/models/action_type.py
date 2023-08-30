from datetime import datetime
from policyapp import db

class ActionType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    bills = db.relationship('Legislation', backref='action_type', lazy=True)