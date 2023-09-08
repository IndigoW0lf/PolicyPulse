from backend import db

class CoSponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    politician_id = db.Column(db.Integer, db.ForeignKey('politician.id'), nullable=False, index=True)

    bill = db.relationship('Bill', back_populates='co_sponsors', lazy=True)
    politician = db.relationship('Politician', back_populates='co_sponsored_bills', lazy=True)

    def __repr__(self):
        return f'<CoSponsor {self.id} - Bill ID: {self.bill_id}, Politician ID: {self.politician_id}>'