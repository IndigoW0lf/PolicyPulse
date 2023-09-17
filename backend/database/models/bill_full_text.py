from datetime import datetime
from backend import db

class BillFullText(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    title = db.Column(db.Text, nullable=True)
    raw_data = db.Column(db.Text, nullable=True)
    bill_metadata = db.Column(db.JSON, nullable=True)
    actions = db.Column(db.JSON, nullable=True)
    sections = db.Column(db.JSON, nullable=True)
    parsing_status = db.Column(db.String(50), nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    
    bill = db.relationship('Bill', back_populates='full_texts', lazy=True)

    def __repr__(self):
        return f'<BillFullText {self.id} - {self.title}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "bill_id": self.bill_id,
            "title": self.title,
            "raw_data": self.raw_data,
            "bill_metadata": self.bill_metadata,
            "actions": self.actions,
            "sections": self.sections,
            "parsing_status": self.parsing_status,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "bill": self.bill.id if self.bill else None,
        }