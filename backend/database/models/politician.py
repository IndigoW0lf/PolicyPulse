from backend import db

class Politician(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True) 
    first_name = db.Column(db.String(255), nullable=True) 
    last_name = db.Column(db.String(255), nullable=True) 
    state = db.Column(db.String(50), nullable=True)
    district = db.Column(db.String(100), nullable=True)
    party = db.Column(db.String(50), nullable=True)
    profile_link = db.Column(db.String(500), nullable=True)
    bioguide_id = db.Column(db.String(50), nullable=True)

    sponsored_amendments = db.relationship('Amendment', back_populates='sponsor', lazy=True)
    sponsored_bills = db.relationship('Bill', back_populates='sponsor', lazy=True)
    co_sponsored_bills = db.relationship('CoSponsor', back_populates='politician', lazy=True)

    def __repr__(self):
        return f'<Politician {self.name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "state": self.state,
            "district": self.district,
            "party": self.party,
            "profile_link": self.profile_link,
            "bioguide_id": self.bioguide_id,
        }
