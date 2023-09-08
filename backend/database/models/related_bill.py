from backend import db

class RelatedBill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    related_bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)

    main_bill = db.relationship('Bill', foreign_keys=[bill_id], back_populates='related_bills', lazy=True)
    related_bill = db.relationship('Bill', foreign_keys=[related_bill_id], back_populates='main_bills', lazy=True)

    def __repr__(self):
        return f'<RelatedBill {self.id}>'