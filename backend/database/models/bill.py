from backend import db
from .committee import bill_committee
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime

class Bill(db.Model):
    """Model representing bills."""
    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(50), nullable=False, unique=True, index=True)
    date_introduced = db.Column(db.Date, nullable=False)
    full_bill_link = db.Column(db.String(300), nullable=False)
    origin_chamber = db.Column(db.String(50), nullable=False)
    sponsor_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False, index=True)
    bill_type = db.Column(db.String(50), nullable=True)
    committee = db.Column(db.String(100), nullable=True)
    congress = db.Column(db.String(50), nullable=True)
    last_action_date = db.Column(db.Date, nullable=True)
    last_action_description = db.Column(db.Text, nullable=True)
    official_title = db.Column(db.String, nullable=True)
    summary = db.Column(db.Text, nullable=False, index=True)
    tags = db.Column(db.String(500), nullable=True, index=True)
    update_date = db.Column(db.Date, nullable=True)
    voting_record = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Timestamp of record creation
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)  # Timestamp of last update
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
    full_texts = db.relationship('BillFullText', back_populates='bill', lazy=True)
    laws = db.relationship('Law', back_populates='bill', lazy=True)
    loc_summary = db.relationship('LOCSummary', back_populates='bill', lazy='joined')
    main_bills = db.relationship('RelatedBill', foreign_keys='RelatedBill.related_bill_id', back_populates='related_bill', lazy=True)
    notes = db.relationship('Note', back_populates='bill', lazy=True)
    policy_areas = db.relationship('PolicyArea', back_populates='bill', lazy=True)
    primary_subject = db.relationship('Subject', back_populates='primary_bills', lazy=True)
    recorded_votes = db.relationship('RecordedVote', back_populates='bill', lazy=True)
    related_bills = db.relationship('RelatedBill', foreign_keys='RelatedBill.bill_id', back_populates='main_bill', lazy=True)
    sponsor = db.relationship('Politician', back_populates='sponsored_bills', lazy=True)
    subjects = db.relationship('Subject', secondary='bill_subject', back_populates='bills', lazy=True)
    titles = db.relationship('BillTitle', back_populates='bill', lazy=True)
    veto_messages = db.relationship('VetoMessage', back_populates='bill', lazy=True)


    def __repr__(self):
        return f'<Bill {self.bill_number}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "official_title": self.official_title,
            "summary": self.summary,
            "date_introduced": self.date_introduced,
            "status": self.status,
            "bill_number": self.bill_number,
            "sponsor_name": self.sponsor_name,
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
            "action_type": self.action_type.to_dict() if self.action_type else None,
            "sponsor": self.sponsor.to_dict(),
            "loc_summary": self.loc_summary.to_dict() if self.loc_summary else None,
            "co_sponsors": [co_sponsor.to_dict() for co_sponsor in self.co_sponsors],
            "committees": [committee.to_dict() for committee in self.committees],
            "actions": [action.to_dict() for action in self.actions],
            "amendments": [amendment.to_dict() for amendment in self.amendments],
            "full_texts": [full_text.to_dict() for full_text in self.full_texts],
            "related_bills": [related_bill.to_dict() for related_bill in self.related_bills],
            "main_bills": [main_bill.to_dict() for main_bill in self.main_bills],
            "subjects": [subject.to_dict() for subject in self.subjects],
            "policy_areas": [policy_area.to_dict() for policy_area in self.policy_areas],
            "veto_messages": [veto_message.to_dict() for veto_message in self.veto_messages],
            "primary_subject": self.primary_subject.to_dict(),
            "recorded_votes": [recorded_vote.to_dict() for recorded_vote in self.recorded_votes],
            "notes": [note.to_dict() for note in self.notes],
            "laws": [law.to_dict() for law in self.laws],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }