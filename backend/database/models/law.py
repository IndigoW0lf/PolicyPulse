from backend import db 
from datetime import datetime

class Law(db.Model):
    __tablename__ = 'law'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(50), nullable=True)
    type = db.Column(db.String(50), nullable=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    
    bill = db.relationship('Bill', back_populates='laws', lazy=True)

    def __repr__(self):
        return f'<Law {self.number} - {self.type}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "number": self.number,
            "type": self.type,
            "bill_id": self.bill_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }