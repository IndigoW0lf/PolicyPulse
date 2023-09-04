from backend import db

class BillFullText(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    title = db.Column(db.Text, nullable=True)
    metadata = db.Column(db.JSON, nullable=True)  # Store metadata as a JSON object
    actions = db.Column(db.JSON, nullable=True)  # Store actions as a JSON object
    sections = db.Column(db.JSON, nullable=True)  # Store sections as a JSON object

    bill = db.relationship('Bill', backref=db.backref('full_texts', lazy=True))
