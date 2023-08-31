from policyapp import db

class RelatedBill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    legislation_id = db.Column(db.Integer, db.ForeignKey('legislation.id'), nullable=False)
    related_bill_id = db.Column(db.Integer, db.ForeignKey('legislation.id'), nullable=False)

    # Relationships
    main_bill = db.relationship('Legislation', foreign_keys=[legislation_id], backref='related_bills', lazy=True)
    related = db.relationship('Legislation', foreign_keys=[related_bill_id], backref='main_bills', lazy=True)
