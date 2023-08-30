from datetime import datetime
from policyapp import db

class Legislation(db.Model):
    # 'Text' types may need to be updated later, but these may be csv, JSON, or other structured formats
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text, nullable=True)
    date_introduced = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(100), nullable=True)
    bill_number = db.Column(db.String(50), nullable=False, unique=True)
    sponsor = db.Column(db.String(200), nullable=False)
    co_sponsors = db.Column(db.Text, nullable=True)  
    committee = db.Column(db.String(200), nullable=True)
    voting_record = db.Column(db.Text, nullable=True) 
    full_text_link = db.Column(db.String(500), nullable=True)
    related_bills = db.Column(db.Text, nullable=True) 
    tags = db.Column(db.String(300), nullable=True)  
    last_action_date = db.Column(db.Date, nullable=True)
    last_action_description = db.Column(db.Text, nullable=True)
    
    # Relationships
    sponsor = db.relationship('Politician', backref='sponsored_bills', lazy=True)
    co_sponsors = db.relationship('CoSponsor', backref='bill', lazy=True)
    related_bills = db.relationship('RelatedBill', backref='main_bill', lazy=True)

class Politician(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    state = db.Column(db.String(50), nullable=True)
    party = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(100), nullable=True)
    profile_link = db.Column(db.String(500), nullable=True)

    # Foreign Key for sponsored bills
    sponsored_bill_id = db.Column(db.Integer, db.ForeignKey('legislation.id'), nullable=True)

class CoSponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    legislation_id = db.Column(db.Integer, db.ForeignKey('legislation.id'), nullable=False)
    politician_id = db.Column(db.Integer, db.ForeignKey('politician.id'), nullable=False)

class RelatedBill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    legislation_id = db.Column(db.Integer, db.ForeignKey('legislation.id'), nullable=False)
    related_bill_id = db.Column(db.Integer, db.ForeignKey('legislation.id'), nullable=False)