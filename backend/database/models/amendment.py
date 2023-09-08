from enum import Enum
from backend import db

class AmendmentStatusEnum(Enum):
    PROPOSED = "Proposed"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"

class Amendment(db.Model):
    """Model representing amendments to bills."""
    id = db.Column(db.Integer, primary_key=True)
    amendment_number = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date_proposed = db.Column(db.Date, nullable=True)
    status = db.Column(db.Enum(AmendmentStatusEnum), nullable=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    
    bill = db.relationship('Bill', back_populates='amendments', lazy=True)

    def __repr__(self):
        return f'<Amendment {self.amendment_number}>'