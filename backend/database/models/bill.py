from backend import db
from .committee import bill_committee
from sqlalchemy.dialects.postgresql import JSON

class Bill(db.Model):
    """Model representing bills."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text, nullable=True)
    date_introduced = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(100), nullable=True)
    bill_number = db.Column(db.String(50), nullable=False, unique=True, index=True)
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
    action_type = db.relationship('ActionType', back_populates='bills', lazy=True)
    sponsor = db.relationship('Politician', back_populates='sponsored_bills', lazy=True)
    loc_summary = db.relationship('LOCSummary', back_populates='bill', lazy='joined')
    co_sponsors = db.relationship('CoSponsor', back_populates='bill', lazy=True)
    committees = db.relationship('Committee', secondary=bill_committee, back_populates='bills')
    actions = db.relationship('Action', back_populates='bill', lazy=True)
    amendments = db.relationship('Amendment', back_populates='bill', lazy=True)
    full_texts = db.relationship('BillFullText', back_populates='bill', lazy=True)
    related_bills = db.relationship('RelatedBill', foreign_keys='RelatedBill.bill_id', back_populates='main_bill', lazy=True)
    main_bills = db.relationship('RelatedBill', foreign_keys='RelatedBill.related_bill_id', back_populates='related_bill', lazy=True)
    subjects = db.relationship('Subject', secondary='bill_subject', back_populates='bills', lazy=True)
    title_type = db.relationship('TitleType', back_populates='bills', lazy=True)

    def __repr__(self):
        return f'<Bill {self.bill_number}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
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
            "title_type_id": self.title_type_id
        }
