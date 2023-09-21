from backend import db
from datetime import datetime
from .committee import bill_committee
from .subcommittee import bill_subcommittee
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Index, text

class Bill(db.Model):
    """Model representing bills."""
    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String, nullable=False, index=True)
    congress = db.Column(db.String, nullable=True)
    date_introduced = db.Column(db.Date, nullable=False)
    origin_chamber = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String, nullable=True)
    title = db.Column(db.String, nullable=False, index=True)
    bill_type = db.Column(db.String, nullable=True)
    committee = db.Column(db.String, nullable=True)
    last_action_date = db.Column(db.Date, nullable=True)                
    last_action_description = db.Column(db.Text, nullable=True)
    update_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Timestamp of record creation
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)  # Timestamp of last update
    tags = db.Column(db.String, nullable=True, index=True)
    full_bill_link = db.Column(db.String, nullable=True)
    voting_record = db.Column(db.Text, nullable=True)
    xml_content = db.Column(JSON, nullable=True)  # Store the XML content as a JSON object
    
    action_type_id = db.Column(db.Integer, db.ForeignKey('action_type.id'), nullable=True)
    primary_subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('politician.id'), nullable=False)
    
    # Relationships
    action_type = db.relationship('ActionType', back_populates='bills', lazy=True)
    actions = db.relationship('Action', back_populates='bill', lazy=True)
    amendments = db.relationship('Amendment', back_populates='bill', lazy=True)
    co_sponsors = db.relationship('CoSponsor', back_populates='bill', lazy=True)
    committees = db.relationship('Committee', secondary=bill_committee, back_populates='bills')
    subcommittees = db.relationship('Subcommittee', secondary=bill_subcommittee, back_populates='bills', lazy=True)
    full_texts = db.relationship('BillFullText', back_populates='bill', lazy=True)
    laws = db.relationship('Law', back_populates='bill', lazy=True)
    loc_summaries = db.relationship('LOCSummary', back_populates='bill', lazy=True)  # Changed attribute name to 'loc_summaries' and removed uselist parameter
    notes = db.relationship('Note', back_populates='bill', lazy=True)
    policy_areas = db.relationship('PolicyArea', back_populates='bill', lazy=True)
    primary_subject = db.relationship('Subject', back_populates='primary_bills', lazy=True)
    recorded_votes = db.relationship('RecordedVote', back_populates='bill', lazy=True)
    related_bills = db.relationship('RelatedBill', back_populates='bill', lazy=True)
    sponsor = db.relationship('Politician', back_populates='sponsored_bills', lazy=True)
    subjects = db.relationship('Subject', secondary='bill_subject', back_populates='bills', lazy=True)
    titles = db.relationship('BillTitle', back_populates='bill', lazy=True)
    
    def __repr__(self):
        return f'<Bill {self.bill_number}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "official_title": self.official_title,
            "date_introduced": self.date_introduced,
            "status": self.status,
            "bill_number": self.bill_number,
            "committee": self.committee,
            "voting_record": self.voting_record,
            "full_bill_link": self.full_bill_link,
            "tags": self.tags,
            "last_action_date": self.last_action_date,
            "last_action_description": self.last_action_description,
            "congress": self.congress,
            "bill_type": self.bill_type,
            "update_date": self.update_date,
            "xml_content": self.xml_content,
            "action_type_id": self.action_type_id,
            "sponsor_id": self.sponsor_id,
            "origin_chamber": self.origin_chamber,
            "primary_subject_id": self.primary_subject_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }