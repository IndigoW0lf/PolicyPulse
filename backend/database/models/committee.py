from backend import db

# Association table for many-to-many relationship between Bill and Committee
bill_committee = db.Table('bill_committee',
    db.Column('bill_id', db.Integer, db.ForeignKey('bill.id'), primary_key=True),
    db.Column('committee_id', db.Integer, db.ForeignKey('committee.id'), primary_key=True)
)

class Committee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    chamber = db.Column(db.String(50), nullable=False)  # e.g., 'House', 'Senate'
    committee_code = db.Column(db.String(50), nullable=False, unique=True)
    
    # Relationships
    bills = db.relationship('Bill', secondary=bill_committee, back_populates='committees')