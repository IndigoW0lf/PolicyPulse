from policyapp import db

class CoSponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    legislation_id = db.Column(db.Integer, db.ForeignKey('legislation.id'), nullable=False)
    politician_id = db.Column(db.Integer, db.ForeignKey('politician.id'), nullable=False)