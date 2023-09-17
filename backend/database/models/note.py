from backend import db

class Note(db.Model):
    __tablename__ = 'note'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    
    bill = db.relationship('Bill', back_populates='notes', lazy=True)

    def __repr__(self):
        return f'<Note {self.id}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "bill_id": self.bill_id,
            "bill": self.bill.id if self.bill else None,
        }