from backend import db

class Committee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    chamber = db.Column(db.String(50), nullable=False)
    committee_code = db.Column(db.String(50), nullable=False, unique=True)
    
    bills = db.relationship('Bill', secondary='bill_committee', back_populates='committees', lazy=True)

    def __repr__(self):
        return f'<Committee {self.name} - {self.chamber}>'

bill_committee = db.Table('bill_committee',
    db.Column('bill_id', db.Integer, db.ForeignKey('bill.id'), primary_key=True),
    db.Column('committee_id', db.Integer, db.ForeignKey('committee.id'), primary_key=True)
)