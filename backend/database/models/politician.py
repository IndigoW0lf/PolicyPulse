from backend import db

class Politician(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    state = db.Column(db.String(50), nullable=True)
    party = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(100), nullable=True)
    profile_link = db.Column(db.String(500), nullable=True)

    # Relationships
    sponsored_bills = db.relationship('Bill', back_populates='sponsor', lazy=True)
    co_sponsored_bills = db.relationship('CoSponsor', backref='politician', lazy=True)