from backend import db
from datetime import datetime

class Committee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    chamber = db.Column(db.String(50), nullable=False)
    committee_code = db.Column(db.String(50), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    
    bills = db.relationship('Bill', secondary='bill_committee', back_populates='committees', lazy=True)

    def __repr__(self):
        return f'<Committee {self.name} - {self.chamber}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "chamber": self.chamber,
            "committee_code": self.committee_code,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


bill_committee = db.Table('bill_committee',
    db.Column('bill_id', db.Integer, db.ForeignKey('bill.id'), primary_key=True),
    db.Column('committee_id', db.Integer, db.ForeignKey('committee.id'), primary_key=True)
)