from backend import db

class BillTitle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    title_type = db.Column(db.String(2), nullable=False)
    title_text = db.Column(db.String(500), nullable=False)
    chamber_code = db.Column(db.String, nullable=True)
    chamber_name = db.Column(db.String, nullable=True)
    
    bill = db.relationship('Bill', back_populates='titles')

    def __repr__(self):
        return f'<BillTitle {self.title_type}: {self.title_text}>'

    def to_dict(self):
        return {
            "id": self.id,
            "title_type": self.title_type,
            "title_text": self.title_text,
            "chamber_code": self.chamber_code,
        }
