from policyapp import db

class RelatedBill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Bill_id = db.Column(db.Integer, db.ForeignKey('Bill.id'), nullable=False)
    related_bill_id = db.Column(db.Integer, db.ForeignKey('Bill.id'), nullable=False)

    # Relationships
    main_bill = db.relationship('Bill', foreign_keys=[Bill_id], backref='related_bills', lazy=True)
    related = db.relationship('Bill', foreign_keys=[related_bill_id], backref='main_bills', lazy=True)
