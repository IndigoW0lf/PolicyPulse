from backend import db
from backend.database.models.committee import bill_committee
from enum import Enum
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
from sqlalchemy import Enum


class ActionType(db.Model):
    """Model representing action types."""
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False, unique=True)
    is_latest = db.Column(db.Boolean, default=False)
    action_type = db.Column(db.String(200), nullable=False)
    
    actions = db.relationship('Action', back_populates='action_type', lazy=True)
    bills = db.relationship('Bill', back_populates='action_type')


action_actioncode = db.Table('action_actioncode',
        db.Column('action_id', db.Integer, db.ForeignKey('action.id'), primary_key=True),
        db.Column('action_code_id', db.Integer, db.ForeignKey('action_code.id'), primary_key=True)
    )

class Action(db.Model):
    """Model representing actions."""
    id = db.Column(db.Integer, primary_key=True)
    action_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    chamber = db.Column(Enum('House', 'Senate', name='chamber_types'), nullable=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    action_type_id = db.Column(db.Integer, db.ForeignKey('action_type.id'), nullable=True, index=True)
    is_latest = db.Column(db.Boolean, default=False)
    
    action_type = db.relationship('ActionType', back_populates='actions', lazy=True)
    bill = db.relationship('Bill', back_populates='actions', lazy=True)
    action_codes = db.relationship('ActionCode', secondary=action_actioncode, back_populates='actions')


class ActionCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    actions = db.relationship('Action', secondary=action_actioncode, back_populates='action_codes')


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
    
    bill = db.relationship('Bill', back_populates='amendments', lazy=True)
    sponsor = db.relationship('Politician', back_populates='amendments', lazy=True)
    
    actions = db.relationship('AmendmentAction', back_populates='amendment', lazy=True)
    amended_bill = db.relationship('AmendedBill', uselist=False, back_populates='amendment', lazy=True)
    links = db.relationship('AmendmentLink', back_populates='amendment', lazy=True)

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

class AmendmentLink(db.Model):
    """Model representing links related to amendments."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=True)
    url = db.Column(db.String(500), nullable=True)
    
    amendment_id = db.Column(db.Integer, db.ForeignKey('amendment.id'), nullable=False)
    amendment = db.relationship('Amendment', back_populates='links')


class BillFullText(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    title = db.Column(db.Text, nullable=True)
    raw_data = db.Column(db.Text, nullable=True)
    bill_metadata = db.Column(db.JSON, nullable=True)
    actions = db.Column(db.JSON, nullable=True)
    sections = db.Column(db.JSON, nullable=True)
    parsing_status = db.Column(db.String(50), nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    
    bill = db.relationship('Bill', back_populates='full_texts', lazy=True)


class BillTitle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    title_type = db.Column(db.String(2), nullable=False)
    title_text = db.Column(db.String(500), nullable=False)
    
    bill = db.relationship('Bill', back_populates='titles')


class Bill(db.Model):
    """Model representing bills."""
    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(50), nullable=False, unique=True, index=True)
    date_introduced = db.Column(db.Date, nullable=False)
    full_bill_link = db.Column(db.String(300), nullable=False)
    origin_chamber = db.Column(db.String(50), nullable=False)
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



class CoSponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    politician_id = db.Column(db.Integer, db.ForeignKey('politician.id'), nullable=False, index=True)
    sponsorship_date = db.Column(db.Date, nullable=True)  # New field to track the date of co-sponsorship
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Timestamp of record creation
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)  # Timestamp of last update

    bill = db.relationship('Bill', back_populates='co_sponsors', lazy=True)
    politician = db.relationship('Politician', back_populates='co_sponsored_bills', lazy=True)


class Committee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    chamber = db.Column(db.String(50), nullable=False)
    committee_code = db.Column(db.String(50), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    
    bills = db.relationship('Bill', secondary='bill_committee', back_populates='committees', lazy=True)

bill_committee = db.Table('bill_committee',
    db.Column('bill_id', db.Integer, db.ForeignKey('bill.id'), primary_key=True),
    db.Column('committee_id', db.Integer, db.ForeignKey('committee.id'), primary_key=True)
)


class Law(db.Model):
    __tablename__ = 'law'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(50), nullable=True)
    type = db.Column(db.String(50), nullable=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    
    bill = db.relationship('Bill', back_populates='laws', lazy=True)


class LOCSummaryCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version_code = db.Column(db.String(50), nullable=False, unique=True)
    chamber = db.Column(db.String(50), nullable=False)
    action_desc = db.Column(db.String(200), nullable=False)
    
    loc_summaries = db.relationship('LOCSummary', back_populates='loc_summary_code', lazy=True)


class LOCSummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    versions = db.Column(db.JSON)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)


class Note(db.Model):
    __tablename__ = 'note'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    
    bill = db.relationship('Bill', back_populates='notes', lazy=True)


class PolicyArea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    bill = db.relationship('Bill', back_populates='policy_areas', lazy=True)


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


class RecordedVote(db.Model):
    __tablename__ = 'recorded_vote'
    id = db.Column(db.Integer, primary_key=True)
    chamber = db.Column(db.String(50), nullable=True)
    congress = db.Column(db.String(50), nullable=True)
    date = db.Column(db.Date, nullable=True)
    full_action_name = db.Column(db.String(200), nullable=True)
    roll_number = db.Column(db.String(50), nullable=True)
    session_number = db.Column(db.String(50), nullable=True)
    url = db.Column(db.String(500), nullable=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    
    bill = db.relationship('Bill', back_populates='recorded_votes', lazy=True)


class RelatedBill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    related_bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)

    main_bill = db.relationship('Bill', foreign_keys=[bill_id], back_populates='related_bills', lazy=True)
    related_bill = db.relationship('Bill', foreign_keys=[related_bill_id], back_populates='main_bills', lazy=True)


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    
    bills = db.relationship('Bill', secondary='bill_subject', back_populates='subjects', lazy=True)
    primary_bills = db.relationship('Bill', back_populates='primary_subject', lazy=True)


bill_subject = db.Table('bill_subject',
    db.Column('bill_id', db.Integer, db.ForeignKey('bill.id'), primary_key=True, index=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True, index=True)
)


class VetoMessage(db.Model):
    """Model representing veto messages."""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=True)
    message = db.Column(db.Text, nullable=True)
    president = db.Column(db.String(200), nullable=True)
    text = db.Column(db.Text, nullable=True)
    
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    bill = db.relationship('Bill', back_populates='veto_messages', lazy=True)