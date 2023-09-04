from backend import db

class CoSponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    politician_id = db.Column(db.Integer, db.ForeignKey('politician.id'), nullable=False)