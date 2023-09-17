from backend import db
from sqlalchemy import Enum

class VetoMessage(db.Model):
    """Model representing veto messages."""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=True)
    message = db.Column(db.Text, nullable=True)
    president = db.Column(db.String(200), nullable=True)
    text = db.Column(db.Text, nullable=True)
    
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    bill = db.relationship('Bill', back_populates='veto_messages', lazy=True)

    def __repr__(self):
        return f'<VetoMessage {self.id} - {self.date} by {self.president}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "message": self.message,
            "president": self.president,
            "text": self.text,
            "bill_id": self.bill_id,
            "bill": self.bill.id if self.bill else None,
        }
