from policyapp import db

class CoSponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)  # Note the lowercase 'bill.id'
    politician_id = db.Column(db.Integer, db.ForeignKey('politician.id'), nullable=False)