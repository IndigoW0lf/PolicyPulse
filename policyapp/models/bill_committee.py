from policyapp import db

# Association table for many-to-many relationship between Bill and Committee
bill_committee = db.Table('bill_committee',
    db.Column('bill_id', db.Integer, db.ForeignKey('bill.id'), primary_key=True),
    db.Column('committee_id', db.Integer, db.ForeignKey('committee.id'), primary_key=True)
)
