from policyapp import db

class Committee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    chamber = db.Column(db.String(50), nullable=False)  # e.g., 'House', 'Senate'
    committee_code = db.Column(db.String(50), nullable=False, unique=True)
    
    # Relationships
    bills = db.relationship('Legislation', secondary='legislation_committee', backref=db.backref('committees', lazy='dynamic'))

# Association table for many-to-many relationship between Legislation and Committee
legislation_committee = db.Table('legislation_committee',
    db.Column('legislation_id', db.Integer, db.ForeignKey('legislation.id'), primary_key=True),
    db.Column('committee_id', db.Integer, db.ForeignKey('committee.id'), primary_key=True)
)