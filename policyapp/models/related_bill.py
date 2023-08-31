from policyapp import db

class RelatedBill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    related_bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)

    # Relationships
    main_bill = db.relationship('bill', foreign_keys=[bill_id], backref='related_bills', lazy=True)
    related = db.relationship('bill', foreign_keys=[related_bill_id], backref='main_bills', lazy=True)
