from backend import db 
from .committee import bill_committee 
from sqlalchemy.dialects.postgresql import JSON

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text, nullable=True)
    date_introduced = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(100), nullable=True)
    bill_number = db.Column(db.String(50), nullable=False, unique=True)
    sponsor_name = db.Column(db.String(200), nullable=False)  
    committee = db.Column(db.String(200), nullable=True)
    voting_record = db.Column(db.Text, nullable=True) 
    full_bill_link = db.Column(db.String(500), nullable=True)
    tags = db.Column(db.String(300), nullable=True)  
    last_action_date = db.Column(db.Date, nullable=True)
    last_action_description = db.Column(db.Text, nullable=True)
    congress = db.Column(db.String(50), nullable=True)  
    bill_type = db.Column(db.String(50), nullable=True)  
    update_date = db.Column(db.Date, nullable=True)
    xml_content = db.Column(JSON, nullable=True)  # Store the XML content as a JSON object
    action_type_id = db.Column(db.Integer, db.ForeignKey('action_type.id'), nullable=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('politician.id'), nullable=False)
    title_type_id = db.Column(db.Integer, db.ForeignKey('title_type.id'), nullable=True)
    
    # Relationships
    sponsor = db.relationship('Politician', back_populates='sponsored_bills', lazy=True)
    loc_summary = db.relationship('LOCSummary', backref='bill', lazy='joined')
    co_sponsors = db.relationship('CoSponsor', backref='bill', lazy=True)
    committees = db.relationship('Committee', secondary=bill_committee, back_populates='bills')