from policyapp import db

class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    chamber = db.Column(db.String(50), nullable=True)  # e.g., "House", "Senate"
    
    # Foreign Key to Legislation
    legislation_id = db.Column(db.Integer, db.ForeignKey('legislation.id'), nullable=False)
    
    # Relationship with Legislation
    legislation = db.relationship('Legislation', backref=db.backref('actions', lazy=True))
