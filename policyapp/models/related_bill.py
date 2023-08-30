from datetime import datetime
from policyapp import db

class RelatedBill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    legislation_id = db.Column(db.Integer, db.ForeignKey('legislation.id'), nullable=False)
    related_bill_id = db.Column(db.Integer, db.ForeignKey('legislation.id'), nullable=False)