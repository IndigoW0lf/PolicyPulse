from datetime import datetime
from policyapp import db
from .committee import bill_committee # Import assoc. table

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text, nullable=True)
    date_introduced = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(100), nullable=True)
    bill_number = db.Column(db.String(50), nullable=False, unique=True)
    sponsor_name = db.Column(db.String(200), nullable=False)  # Renamed from 'sponsor' to avoid confusion
    committee = db.Column(db.String(200), nullable=True)
    voting_record = db.Column(db.Text, nullable=True) 
    full_text_link = db.Column(db.String(500), nullable=True)
    tags = db.Column(db.String(300), nullable=True)  
    last_action_date = db.Column(db.Date, nullable=True)
    last_action_description = db.Column(db.Text, nullable=True)
    congress = db.Column(db.String(50), nullable=True)  # New column to capture which Congress the bill belongs to
    bill_type = db.Column(db.String(50), nullable=True)  # New column to capture the type of the bill (e.g., HR, S, etc.)
    
    action_type_id = db.Column(db.Integer, db.ForeignKey('action_type.id'), nullable=True)
    loc_summary_id = db.Column(db.Integer, db.ForeignKey('loc_summary.id'), nullable=True)
    
    # Relationships
    sponsor = db.relationship('Politician', backref='sponsored_bills', lazy=True)
    co_sponsors = db.relationship('CoSponsor', backref='bill', lazy=True)
    related_bills = db.relationship('RelatedBill', backref='main_bill', lazy=True)
    committees = db.relationship('Committee', secondary=bill_committee, backref=db.backref('bills', lazy='dynamic'))
