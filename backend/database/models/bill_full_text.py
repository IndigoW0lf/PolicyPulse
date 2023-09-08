from backend import db

class BillFullText(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    title = db.Column(db.Text, nullable=True)
    meta_data = db.Column(db.JSON, nullable=True)
    actions = db.Column(db.JSON, nullable=True)
    sections = db.Column(db.JSON, nullable=True)
    
    bill = db.relationship('Bill', back_populates='full_texts', lazy=True)

    def __repr__(self):
        return f'<BillFullText {self.id} - {self.title}>'