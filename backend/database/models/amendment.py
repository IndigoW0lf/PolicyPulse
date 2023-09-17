from enum import Enum
from backend import db

class Amendment(db.Model):
    """Model representing amendments to bills."""
    id = db.Column(db.Integer, primary_key=True)
    amendment_number = db.Column(db.String(50), nullable=False)
    congress = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    latest_action_date = db.Column(db.Date, nullable=True)
    latest_action_text = db.Column(db.Text, nullable=True)
    purpose = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(50), nullable=True)

    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('politician.id'), nullable=True)

    sponsor = db.relationship('Politician', back_populates='sponsored_amendments', lazy=True)
    bill = db.relationship('Bill', back_populates='amendments', lazy=True)
    actions = db.relationship('AmendmentAction', back_populates='amendment', lazy=True)
    amended_bill = db.relationship('AmendedBill', uselist=False, back_populates='amendment', lazy=True)
    links = db.relationship('AmendmentLink', back_populates='amendment', lazy=True)

    def __repr__(self):
        return f'<Amendment {self.amendment_number}>'

    def to_dict(self):
        return {
            "id": self.id,
            "amendment_number": self.amendment_number,
            "congress": self.congress,
            "description": self.description,
            "latest_action_date": self.latest_action_date,
            "latest_action_text": self.latest_action_text,
            "purpose": self.purpose,
            "type": self.type,
            "status": self.status,
            "bill_id": self.bill_id,
            "sponsor_id": self.sponsor_id,
        }

class AmendmentAction(db.Model):
    """Model representing actions on amendments."""
    id = db.Column(db.Integer, primary_key=True)
    action_code = db.Column(db.String(50), nullable=True)
    action_date = db.Column(db.Date, nullable=True)
    action_time = db.Column(db.String(20), nullable=True)
    committee_name = db.Column(db.String(200), nullable=True)
    committee_system_code = db.Column(db.String(50), nullable=True)
    source_system_code = db.Column(db.String(10), nullable=True)
    source_system_name = db.Column(db.String(200), nullable=True)
    action_text = db.Column(db.Text, nullable=True)
    
    amendment_id = db.Column(db.Integer, db.ForeignKey('amendment.id'), nullable=False)
    amendment = db.relationship('Amendment', back_populates='actions')

    def __repr__(self):
        return f'<AmendmentAction {self.id}>'

    def to_dict(self):
        return {
            "id": self.id,
            "action_code": self.action_code,
            "action_date": self.action_date,
            "action_time": self.action_time,
            "committee_name": self.committee_name,
            "committee_system_code": self.committee_system_code,
            "source_system_code": self.source_system_code,
            "source_system_name": self.source_system_name,
            "action_text": self.action_text,
        }

class AmendedBill(db.Model):
    """Model representing bills amended by amendments."""
    id = db.Column(db.Integer, primary_key=True)
    congress = db.Column(db.String(50), nullable=True)
    number = db.Column(db.String(50), nullable=True)
    origin_chamber = db.Column(db.String(50), nullable=True)
    origin_chamber_code = db.Column(db.String(50), nullable=True)
    title = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(50), nullable=True)
    
    amendment_id = db.Column(db.Integer, db.ForeignKey('amendment.id'), nullable=False)
    amendment = db.relationship('Amendment', back_populates='amended_bill')

    def __repr__(self):
        return f'<AmendedBill {self.id}>'

    def to_dict(self):
        return {
            "id": self.id,
            "congress": self.congress,
            "number": self.number,
            "origin_chamber": self.origin_chamber,
            "origin_chamber_code": self.origin_chamber_code,
            "title": self.title,
            "type": self.type,
        }


class AmendmentLink(db.Model):
    """Model representing links related to amendments."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=True)
    url = db.Column(db.String(500), nullable=True)
    
    amendment_id = db.Column(db.Integer, db.ForeignKey('amendment.id'), nullable=False)
    amendment = db.relationship('Amendment', back_populates='links')

    def __repr__(self):
        return f'<AmendmentLink {self.id}>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
        }