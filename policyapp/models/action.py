from policyapp import db

class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    chamber = db.Column(db.String(50), nullable=True)  # e.g., "House", "Senate"
    
     # Foreign Key to Bill
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    
    # Foreign Key to ActionType
    action_type_id = db.Column(db.Integer, db.ForeignKey('action_type.id'), nullable=True)
    
    # Relationship with Bill
    bill = db.relationship('Bill', backref=db.backref('actions', lazy=True))
    
    # Relationship with ActionType
    action_type = db.relationship('ActionType', backref=db.backref('actions', lazy=True))