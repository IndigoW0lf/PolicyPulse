from backend import db
from datetime import datetime

class Subcommittee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    subcommittee_code = db.Column(db.String(255), nullable=False, unique=True)
    activity_name = db.Column(db.String(1000), nullable=True)
    activity_date = db.Column(db.Date, nullable=True)
    committee_id = db.Column(db.Integer, db.ForeignKey('committee.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)

    bills = db.relationship('Bill', secondary='bill_subcommittee', back_populates='subcommittees', lazy=True)

    def __repr__(self):
        return f'<Subcommittee {self.name}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "subcommittee_code": self.subcommittee_code,
            "activity_name": self.activity_name,
            "activity_date": self.activity_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


bill_subcommittee = db.Table('bill_subcommittee',
    db.Column('bill_id', db.Integer, db.ForeignKey('bill.id'), primary_key=True),
    db.Column('subcommittee_id', db.Integer, db.ForeignKey('subcommittee.id'), primary_key=True)
)
