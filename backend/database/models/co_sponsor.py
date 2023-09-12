from datetime import datetime
from backend import db

class CoSponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    politician_id = db.Column(db.Integer, db.ForeignKey('politician.id'), nullable=False, index=True)
    sponsorship_date = db.Column(db.Date, nullable=True)  # New field to track the date of co-sponsorship
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Timestamp of record creation
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)  # Timestamp of last update

    bill = db.relationship('Bill', back_populates='co_sponsors', lazy=True)
    politician = db.relationship('Politician', back_populates='co_sponsored_bills', lazy=True)

    def __repr__(self):
        return f'<CoSponsor {self.id} - Bill ID: {self.bill_id}, Politician ID: {self.politician_id}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "bill_id": self.bill_id,
            "politician_id": self.politician_id,
            "sponsorship_date": self.sponsorship_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "bill": self.bill.to_dict() if self.bill else None,
            "politician": self.politician.to_dict() if self.politician else None,
        }