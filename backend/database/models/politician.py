from backend import db

class Politician(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)  # New name column
    state = db.Column(db.String(50), nullable=True)
    party = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(100), nullable=True)
    profile_link = db.Column(db.String(500), nullable=True)
    bioguide_id = db.Column(db.String(50), nullable=True)
    gpo_id = db.Column(db.String(50), nullable=True)
    lis_id = db.Column(db.String(50), nullable=True)

    sponsored_bills = db.relationship('Bill', back_populates='sponsor', lazy=True)
    co_sponsored_bills = db.relationship('CoSponsor', back_populates='politician', lazy=True)

    def __repr__(self):
        return f'<Politician {self.name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,  # Updated to reflect the new name column
            "state": self.state,
            "party": self.party,
            "role": self.role,
            "profile_link": self.profile_link,
            "bioguide_id": self.bioguide_id,
            "gpo_id": self.gpo_id,
            "lis_id": self.lis_id,
            "sponsored_bills": [bill.to_dict() for bill in self.sponsored_bills],
            "co_sponsored_bills": [co_sponsor.to_dict() for co_sponsor in self.co_sponsored_bills],
        }