from policyapp import db

class RelatedBill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    related_bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)

    # Relationships
    main_bill = db.relationship('Bill', foreign_keys=[bill_id], lazy=True, backref='related_bills')
    related = db.relationship('Bill', foreign_keys=[related_bill_id], lazy=True, backref='main_bills')
